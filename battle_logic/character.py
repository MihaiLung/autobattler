from battle_logic.animations.destroy_animation import DeathAnimation
from battle_logic.character_settings.minion_stats import elf_stats, orc_stats
from settings import *
from battle_logic.character_settings.minion_base_class import MinionStats
import math
import enum
from typing import Optional
from dataclasses import dataclass
import numpy as np

from battle_logic.logic.utils import sprite_distance, get_closest_target
from utils import get_asset_path, tdiff

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


class AttackManager:
    def __init__(self, attacker: 'Character', target: 'Character', splash: int = 1) -> None:

        self.attacker = attacker
        self.target = target

        self.direction_to_target = (attacker.central_position_for_collision - target.central_position_for_collision).normalize()

        self.step_count: int = 0
        self.num_frames_forward: int = 5
        self.num_frames_backward: int = 30
        self.speed_forward = self.attacker.diameter * 0.2 / self.num_frames_forward

        # Reverse engineer what this needs to be for the end position to be exactly the start position
        self.speed_backward = self.speed_forward*self.num_frames_forward/self.num_frames_backward

        self.splash = splash
        self.enemies_group = self.target.own_group
        # if self.splash:
        #     print(len(self.enemies_group))


    def update(self):
        self.step_count += 1
        if self.step_count <= self.num_frames_forward:
            if self.step_count == self.num_frames_forward:
                if self.splash>1:
                    contact_rect = self.target.rect.copy().inflate(200,200)
                    # print(contact_rect)
                    enemies_in_range = []
                    for enemy in self.enemies_group.sprites():
                        if enemy.rect.colliderect(contact_rect):
                            enemies_in_range.append(enemy)

                    hit_enemies = sorted(enemies_in_range, key=lambda e: sprite_distance(e, self.attacker))[:self.splash]
                    damage = self.attacker.stats.attack/max(len(hit_enemies),1)
                    print(damage)
                    for enemy in hit_enemies:
                        enemy.take_damage(damage)

                else:
                    self.target.take_damage(self.attacker.stats.attack)
                    # self.target.update_image()
            return -self.direction_to_target*self.speed_forward
        elif self.step_count <= self.num_frames_forward+ self.num_frames_backward:
            return self.direction_to_target*self.speed_backward
        else:
            return None



class Character(pygame.sprite.Sprite):
    LONGEST_ATTACK_INTERVAL = 360


    def __init__(self, stats: MinionStats, own_group: Optional[CharacterGroup]=None, enemy_group: Optional[CharacterGroup]=None, image_raw: Optional[pygame.Surface] = None):
        super().__init__()
        # Save stats
        self.stats = stats
        self.diameter = stats.size * SCALE
        self.image_path = stats.image_loc
        self.own_group = own_group
        self.enemy_group = enemy_group

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
        self.attack_speed = stats.attack_speed
        self.attack_timer = Character.LONGEST_ATTACK_INTERVAL/self.attack_speed
        self.frames_until_attack_allowed = 0

        # Initialize sprite state
        self.current_action = CharacterActions.IDLE
        self.target = None
        self.next_move = pygame.Vector2(0,0)
        self.last_move = pygame.Vector2(0,0)
        self.willingness_to_move = 1
        self.attack_manager: Optional[AttackManager] = None

        if stats.abilities:
            self.abilities = [ability(self) for ability in stats.abilities]
        else:
            self.abilities = []

    def recompute_attack_timer(self):
        current_attack_timer = self.attack_timer
        self.attack_timer = Character.LONGEST_ATTACK_INTERVAL/self.attack_speed

        # If a character's attack speed changes, apply the change to their current timer too (more responsive)
        attack_timer_diff = current_attack_timer-self.attack_timer
        self.frames_until_attack_allowed -= attack_timer_diff

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
        return self.get_collision_position+pygame.Vector2(self.diameter / 2, self.diameter / 2)

    def set_position_center(self, central_position: tuple[int, int]):
        self.rect.center = central_position
        self.position = pygame.Vector2(self.rect.topleft)

    def set_position_topleft(self, topleft_position: tuple[int, int]):
        self.rect.topleft = topleft_position
        self.position = pygame.Vector2(self.rect.topleft)


    def load_image(self):
        self.image_raw = pygame.image.load(get_asset_path(self.stats.image_loc)).convert_alpha()
        self.image_raw = pygame.transform.smoothscale(self.image_raw, (self.diameter, self.diameter))
        self.image = self.image_raw.copy()


    def copy(self):
        return Character(self.stats, self.own_group, self.enemy_group, self.image_raw.copy())

    def get_quadrant(self):
        quadrant_vector = pygame.Vector2(self.rect.center) / COLLISION_QUADRANT_SIZE
        return (int(quadrant_vector[0]), int(quadrant_vector[1]))

    def update_image(self):

        self.image = self.image_raw.copy()
        health_prop = self.current_health/self.starting_health

        if health_prop<1:
            bar_width = self.diameter * 0.9
            bar_offset = self.diameter * 0.05
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
        self.update_image()

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
            return DeathAnimation(self, 10, 10)

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
                self.last_move = self.next_move = pygame.Vector2(0, 0)
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
                    self.attack_manager = AttackManager(self, self.target, self.stats.splash_limit)
            else:
                self.move_towards(self.target.rect)
        if self.frames_until_attack_allowed>0:
            self.frames_until_attack_allowed -= 1

        for ability in self.abilities:
            ability.update()
        return None


    @property
    def proposed_next_rect(self):
        return self.rect.move(self.next_move)

    @property
    def proposed_next_position(self):
        return self.position+self.next_move

    def update_rect_position(self):
        # High interpolation value = more momentum
        # angle = self.last_move.angle_to(self.next_move)
        # valid_move = min(angle, 360-angle)<45
        valid_move = self.next_move.magnitude()>self.speed*0.1
        if valid_move or self.willingness_to_move==0:
            actual_move = self.next_move.lerp(self.last_move, 0.1)
            actual_move = self.next_move
            if actual_move.magnitude()>self.speed:
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
        # else:
        #     self.last_move = pygame.Vector2(0, 0)

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



@dataclass
class DamageAction:
    origin: Character
    target: Character # Default value