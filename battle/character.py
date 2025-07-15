import pygame

from character_settings.minion_stats import elf_stats, orc_stats
from settings import *
import random
from character_settings.minion_base_class import MinionStats
import math
import enum
from typing import Optional
from dataclasses import dataclass
import numpy as np

from logic.utils import sprite_distance, get_random_point_in_rect, yield_array_elements, get_closest_target

FONT = pygame.font.SysFont(None, int(30*SCALE))


class CharacterGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def set_targets(self, target_group):
        pairings = {}
        for s in self:
            # Find t in target_group with min distance to s
            s.set_target(get_closest_target(s, target_group))

    def update_rect_position(self):
        for s in self:
            s.update_rect_position()

class CharacterActions(enum.Enum):
    ATTACKING = "attacking"
    IDLE = "idle"
    MOVING = "moving"

scale = elf_stats.attack*10*SCALE
attack_image_elf = pygame.image.load("assets/sword_slice.png").convert_alpha()
attack_image_elf = pygame.transform.smoothscale(attack_image_elf, (scale, scale))

scale = orc_stats.attack*5*SCALE
attack_image_orc = pygame.image.load("assets/smoke_evil.png").convert_alpha()
attack_image_orc = pygame.transform.smoothscale(attack_image_orc, (scale, scale))
attack_image_orc = pygame.transform.flip(attack_image_orc, True, False)

# class AttackImpactSprite(pygame.sprite.Sprite):
#     def __init__(self, attack_image, schedule=(3,30,30), target: Optional['Character']=None, damage: Optional[int] = None):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = attack_image.copy()
#         self.rect = self.image.get_rect()
#         self.schedule = schedule
#         self.step = 0
#
#         alphas = np.concat((
#             np.linspace(0, 140, schedule[0]),
#             np.linspace(140, 140, schedule[1]),
#             np.linspace(140, 0, schedule[2]),
#         ))
#         self.iterator = yield_array_elements(alphas)
#         self.target = target
#         self.damage = damage
#
#
#     def create_new_instance(self, attack_impact_location, target, damage):
#         new_attack = AttackImpactSprite(self.image, self.schedule, target, damage)
#         new_attack.rect.center = get_random_point_in_rect(attack_impact_location)
#         return new_attack
#
#     def set_target(self, target: 'Character'):
#         self.target = target
#
#     def yield_next_alpha(self):
#         try:
#             return next(self.iterator)
#         except StopIteration:
#             return None
#
#     def update(self):
#         self.step += 1
#         # impact = False
#         if self.step == self.schedule[0]:
#             self.target.take_damage(self.damage)
#             self.target.update_image()
#         alpha = self.yield_next_alpha()
#         # print(alpha)
#         if alpha is not None:
#             self.image.set_alpha(int(alpha))
#             pass
#         else:
#             self.kill()
#         # return impact


#
# elf_attack = AttackImpactSprite(attack_image_elf)
# orc_attack = AttackImpactSprite(attack_image_orc)

class AttackManager:
    def __init__(self, attacker: 'Character', target: 'Character') -> None:

        self.attacker = attacker
        self.target = target

        self.direction_to_target = (attacker.central_position_for_collision - target.central_position_for_collision).normalize()

        self.step_count: int = 0
        self.num_frames_forward: int = 5
        self.num_frames_backward: int = 30
        self.speed_forward = self.attacker.radius*0.2/self.num_frames_forward

        # Reverse engineer what this needs to be for the end position to be exactly the start position
        self.speed_backward = self.speed_forward*self.num_frames_forward/self.num_frames_backward


    def update(self):
        self.step_count += 1
        if self.step_count <= self.num_frames_forward:
            if self.step_count == self.num_frames_forward:
                self.target.take_damage(self.attacker.stats.attack)
                self.target.update_image()
            return -self.direction_to_target*self.speed_forward
        elif self.step_count <= self.num_frames_forward+ self.num_frames_backward:
            return self.direction_to_target*self.speed_backward
        else:
            return None




class Character(pygame.sprite.Sprite):
    LONGEST_ATTACK_INTERVAL = 300
    def __init__(self, stats: MinionStats, image_raw: Optional[pygame.Surface] = None):
        super().__init__()
        # Save stats
        self.stats = stats
        self.radius = stats.size*SCALE

        # Initialize sprite visuals
        if image_raw is None:
            self.load_image()
        else:
            self.image_raw = image_raw
            self.image = self.image_raw.copy()

        # Initialize position
        self.rect = self.image.get_rect()
        self.collision_rect = self.rect.copy()
        self.position = pygame.Vector2(self.rect.topleft)
        self.collision_position = self.position.copy()

        # Initialize sprite stats
        self.speed = stats.movement_speed*SCALE
        self.starting_health = stats.health
        self.current_health = stats.health
        self.update_image()
        self.attack_timer = Character.LONGEST_ATTACK_INTERVAL/self.stats.attack_speed
        self.frames_until_attack_allowed = 0

        # Initialize sprite state
        self.current_action = CharacterActions.IDLE
        self.target = None
        self.next_move = pygame.Vector2(0,0)
        self.last_move = pygame.Vector2(0,0)
        self.willingness_to_move = 1
        self.attack_manager: Optional[AttackManager] = None

        # # Set attack image
        # if self.stats is orc_stats:
        #     self.attack_image = orc_attack
        # else:
        #     self.attack_image = elf_attack

    @property
    def collision_resolution_priority(self):
        """
        For collision resolution; sprites STANDING ON BUSINESS get highest priority, further away flops wait for their
        gdam turn
        :return:
        """
        if self.target:
            return self.distance_from_target
        else:
            return np.inf


    @property
    def get_collision_position(self)->pygame.Vector2:
        """
        When resolving collisions, check which rect should be used.
        Relevant context - when performing the attack animations, sprites do a little animation where the visual
        involves the sprite moving, but collision shouldn't be impacted by it. So while attacking, store the position
        just before attacking and use that to continue ensuring collision works, but otherwise use the sprite's regular
        rect.
        """
        if self.current_action == CharacterActions.ATTACKING:
            return self.collision_position
        else:
            return self.position

    @property
    def central_position_for_collision(self):
        return self.get_collision_position+pygame.Vector2(self.radius/2, self.radius/2)

    def set_position_center(self, central_position: tuple[int, int]):
        self.rect.center = central_position
        self.position = pygame.Vector2(self.rect.topleft)

    def set_position_topleft(self, topleft_position: tuple[int, int]):
        self.rect.topleft = topleft_position
        self.position = pygame.Vector2(self.rect.topleft)



    def load_image(self):
        self.image_raw = pygame.image.load(self.stats.image_loc).convert_alpha()
        self.image_raw = pygame.transform.smoothscale(self.image_raw, (self.radius, self.radius))
        self.image = self.image_raw.copy()


    def copy(self):
        return Character(self.stats, self.image_raw.copy())

    def get_quadrant(self):
        quadrant_vector = pygame.Vector2(self.rect.center)/QUADRANT_SIZE
        return (int(quadrant_vector[0]), int(quadrant_vector[1]))

    def update_image(self):
        # # Create a fresh copy so we never draw over the original
        # self.image = self.image_raw.copy()
        #
        # # Prepare stat texts
        # health_surf = FONT.render(str(self.current_health), True, (255, 0, 0))
        # attack_surf = FONT.render(str(self.stats.attack), True, (0, 0, 0))
        #
        # # Position: health bottom-left, attack bottom-right
        # health_pos = 3, self.image.get_height() - health_surf.get_height() - 3
        # attack_pos = self.image.get_width() - attack_surf.get_width() - 3, \
        #              self.image.get_height() - attack_surf.get_height() - 3
        #
        # # Overlay numbers
        # self.image.blit(health_surf, health_pos)
        # self.image.blit(attack_surf, attack_pos)

        self.image = self.image_raw.copy()
        health_prop = self.current_health/self.starting_health

        if health_prop<1:
            bar_width = self.radius*0.9
            bar_offset = self.radius*0.05
            remaining_health_width = int(bar_width*health_prop)
            remaining_health_rect = pygame.Rect(bar_offset, 0, remaining_health_width, 10*SCALE)

            lost_health_width = int(bar_width*(1-health_prop))
            lost_health_rect = pygame.Rect(remaining_health_width+bar_offset, 0, lost_health_width, 10*SCALE)

            pygame.draw.rect(self.image, 'green', remaining_health_rect)
            pygame.draw.rect(self.image, 'red', lost_health_rect)




    def deal_damage(self, target: 'Character'):
        target.current_health -= self.stats.attack-target.stats.armour

    def take_damage(self, damage: float):
        self.current_health -= damage-self.stats.armour

    def set_target(self, target: 'Character'):
        self.target = target

    @property
    def distance_from_target(self):
        return sprite_distance(self.target, self)

    def move_no_collision(self, move):
        self.position += move
        self.update_rect_position()

    def update(self):
        """
        This function:
        1. Kills the sprite when health goes below 0
        2. Switches between attack and move modes
        3. Proposes ideal next move action (which is to be updated later by collision resolution)
        """
        if self.current_health <= 0:
            self.kill()
            return "dead"

        # Handle attack
        if self.current_action == CharacterActions.ATTACKING:
            next_action = self.attack_manager.update()
            if next_action is not None:
                self.move_no_collision(next_action)
            else:
                self.current_action = CharacterActions.IDLE
                # self.willingness_to_move = 1
                del self.attack_manager
                self.position = self.collision_position.copy()
            self.frames_until_attack_allowed -= 1

        elif self.current_action == CharacterActions.IDLE:
            if self.target is None:
                pass
            else:
                self.current_action = CharacterActions.MOVING
        elif self.current_action == CharacterActions.MOVING:
            if self.distance_from_target < 0.1:
                if self.frames_until_attack_allowed<=0:
                    self.current_action = CharacterActions.ATTACKING
                    self.willingness_to_move = 0
                    self.last_move = pygame.Vector2(0,0)
                    self.next_move = pygame.Vector2(0,0)
                    self.collision_position = self.position.copy()
                    self.frames_until_attack_allowed = self.attack_timer
                    self.attack_manager = AttackManager(self, self.target)
            else:
                self.move_towards(self.target.rect)
        if self.frames_until_attack_allowed>0:
            self.frames_until_attack_allowed -= 1
        return None






        # if self.current_action == CharacterActions.ATTACKING:
        #     impact = self.active_animator.update()
        #     if impact:
        #         return DamageAction(self, self.target)
        #     if self.active_animator.is_finished:
        #         self.current_action = CharacterActions.IDLE
        #         self.active_animator = None
        #
        #     # else:
        #     #     self.next_move = self.active_animator.attack_direction
        # else:
        #     self.collision_enabled = True
        #     self.current_action = CharacterActions.MOVING
        #     if self.distance_from_target < 0.1:
        #         self.current_action = CharacterActions.ATTACKING
        #         self.collision_enabled = False
        #         self.last_move = pygame.Vector2(0,0)
        #         self.next_move = pygame.Vector2(0,0)
        #         return self.attack_image.create_new_instance(self.target.rect)
        #     else:
        #         self.move_towards(self.target.rect)
        # return None



    def randomize_location(self):
        if "elf" in self.stats.image_loc:
            x = random.uniform(100, WIDTH//2-100)
            y = random.uniform(100, HEIGHT-100)
        else:
            x = random.uniform(WIDTH//2+100, WIDTH-100)
            y = random.uniform(100, HEIGHT-100)
        self.position = pygame.Vector2(int(x), int(y))
        self.rect.topleft = self.position


    @property
    def proposed_next_rect(self):
        return self.rect.move(self.next_move)

    @property
    def proposed_next_position(self):
        return self.position+self.next_move

    # def predicted_next_quadrant(self):


    def control_angle(self, move: pygame.Vector2, angular_momentum=10):
        if self.last_move.magnitude()==0:
            return move
        else:
            angle = move.angle_to(self.last_move)
            capped_angle = min(angle, 360-angle)
            if capped_angle<angular_momentum:
                return move.project(self.last_move.rotate(angle))
            else:
                direction = -1 if angle==capped_angle else 1
                return move.rotate(direction*capped_angle)

    def update_rect_position(self):
        # High interpolation value = more momentum
        if (self.next_move.magnitude()>self.speed*0.3) or self.willingness_to_move==0:
            actual_move = self.next_move.lerp(self.last_move, 0.3)

            # actual_move = self.control_angle(actual_move)

            if actual_move.magnitude()>=0.1:
                actual_move.clamp_magnitude_ip(self.speed)
            self.last_move = actual_move
            self.position += actual_move
            self.rect.topleft = (int(self.position.x), int(self.position.y))
            if self.rect.top<0:
                self.rect.top=0
                # self.momentum[1] = max(self.momentum[1], 0)
            if self.rect.bottom>HEIGHT:
                self.rect.bottom=HEIGHT
                # self.momentum[1] = min(self.momentum[1], 0)
            if self.rect.left<0:
                self.rect.left=0
                # self.momentum[0] = max(self.momentum[0], 0)
            if self.rect.right>WIDTH:
                self.rect.right=WIDTH
                # self.momentum[0] = min(self.momentum[0], 0)


    # ACTION - move towards
    def move_towards(self, target_rect):
        self.willingness_to_move = 1
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        direction = pygame.Vector2(dx, dy)
        dist = math.hypot(dx, dy)
        if dist > 0.01:
            velocity = direction.normalize()*self.speed
            self.next_move = velocity

    def draw(self, screen, centered_on):
        draw_rect = self.rect.copy()
        draw_rect.center = centered_on
        screen.blit(self.image, draw_rect)
    #
    # def attack(self, target_rect: pygame.Rect):
    #     # Update character state to attacking
    #     self.current_action = CharacterActions.ATTACKING
    #     self.attack_direction = pygame.Vector2(target_rect.x-self.rect.x, target_rect.y-self.rect.y)


@dataclass
class DamageAction:
    origin: Character
    target: Character # Default value