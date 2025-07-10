import pygame
from settings import *
import random
from minions.minion_base_class import MinionStats
import math
import enum
from typing import Optional
from dataclasses import dataclass

FONT = pygame.font.SysFont(None, 30)


class CharacterActions(enum.Enum):
    ATTACKING = "attacking"
    IDLE = "idle"
    MOVING = "moving"


class Coordinator:
    def __init__(self):
        pass


class AttackAnimator(Coordinator):
    def __init__(self, target_direction: pygame.math.Vector2, speed: float):
        super().__init__()
        self.is_finished = False
        self.step = 0
        self.target_direction = target_direction
        if self.target_direction.magnitude() > 0:
            self.target_direction = target_direction.normalize()*speed
        self.attack_direction = None

    def update(self):

        # Wind up attack
        impact = False
        # if self.step < 20:
        #     self.attack_direction = 0*self.target_direction
        # # Perform attack
        # elif self.step < 27:
        #     self.attack_direction = 4*self.target_direction
        # elif self.step == 27:
        #     impact = True
        # elif self.step < 40:
        #     self.attack_direction = 3*self.target_direction
        # elif self.step < 60:
        #     self.attack_direction = 0*self.target_direction
        # else:
        #     self.is_finished = True
        #     self.attack_direction = None
        self.attack_direction = 0*self.target_direction
        self.step += 1
        if self.step==30:
            impact = True
        if self.step==60:
            self.is_finished = True
        return impact



class Character(pygame.sprite.Sprite):
    def __init__(self, stats: MinionStats, camera):
        super().__init__(camera)
        # Save stats
        self.stats = stats

        # Initialize sprite visuals
        self.image_raw = pygame.image.load(stats.image_loc).convert_alpha()
        self.image_raw = pygame.transform.smoothscale(self.image_raw, (stats.size*SCALE, stats.size*SCALE))
        self.image = self.image_raw.copy()
        self.rect = self.image.get_rect()
        self.position = pygame.Vector2(self.rect.topleft)
        self.randomize_location()

        # Initialize sprite stats
        self.speed = stats.movement_speed*SCALE
        self.current_health = stats.health
        self.update_image()

        # Initialize sprite state
        self.current_action = CharacterActions.IDLE
        self.active_animator: Optional[AttackAnimator] = None
        self.target = None
        # self.momentum = pygame.math.Vector2(0,0)

    def get_quadrant(self):
        quadrant_vector = pygame.Vector2(self.rect.center)/QUADRANT_SIZE
        return (int(quadrant_vector[0]), int(quadrant_vector[1]))

    def update_image(self):
        # Create a fresh copy so we never draw over the original
        self.image = self.image_raw.copy()

        # Prepare stat texts
        health_surf = FONT.render(str(self.current_health), True, (255, 0, 0))
        attack_surf = FONT.render(str(self.stats.attack), True, (0, 0, 0))

        # Position: health bottom-left, attack bottom-right
        health_pos = 3, self.image.get_height() - health_surf.get_height() - 3
        attack_pos = self.image.get_width() - attack_surf.get_width() - 3, \
                     self.image.get_height() - attack_surf.get_height() - 3

        # Overlay numbers
        self.image.blit(health_surf, health_pos)
        self.image.blit(attack_surf, attack_pos)

    def damage(self, target: 'Character'):
        target.current_health -= self.stats.attack-target.stats.armour

    def set_target(self, target: 'Character'):
        self.target = target


    def update(self):
        if self.current_health <= 0:
            self.kill()
            return "dead"
        if self.current_action == CharacterActions.ATTACKING:
            impact = self.active_animator.update()
            if impact:
                return DamageAction(self, self.target)
            if self.active_animator.is_finished:
                self.current_action = CharacterActions.IDLE
                self.active_animator = None

            else:
                self.apply_force_to_object(self.active_animator.attack_direction)
        else:
            self.current_action = CharacterActions.MOVING
            self.move_towards(self.target.rect)
            if self.rect.colliderect(self.target.rect):
                self.current_action = CharacterActions.ATTACKING
                target_direction = pygame.Vector2(self.target.rect.topleft)-pygame.Vector2(self.rect.topleft)
                self.active_animator = AttackAnimator(target_direction, self.speed)
        return None



    def randomize_location(self):
        if "elf" in self.stats.image_loc:
            x = random.uniform(100, WIDTH//2-100)
            y = random.uniform(100, HEIGHT//2-100)
        else:
            x = random.uniform(WIDTH//2+100, WIDTH-100)
            y = random.uniform(HEIGHT//2+100, HEIGHT-100)
        self.position = pygame.Vector2(int(x), int(y))
        self.rect.topleft = self.position


    def apply_force_to_object(self, direction: pygame.math.Vector2):
        if direction.magnitude() > 0.01:
            self.position += direction
            self.update_rect_position()

    def update_rect_position(self):
        self.rect.topleft = (int(self.position.x), int(self.position.y))
        if self.rect.top<0:
            self.rect.top=0
            self.momentum[1] = max(self.momentum[1], 0)
        if self.rect.bottom>HEIGHT:
            self.rect.bottom=HEIGHT
            self.momentum[1] = min(self.momentum[1], 0)
        if self.rect.left<0:
            self.rect.left=0
            self.momentum[0] = max(self.momentum[0], 0)
        if self.rect.right>WIDTH:
            self.rect.right=WIDTH
            self.momentum[0] = min(self.momentum[0], 0)


    # def object_self_movement(self, direction: pygame.math.Vector2):

    # ACTION - move towards
    def move_towards(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        direction = pygame.Vector2(dx, dy)
        dist = math.hypot(dx, dy)
        if dist > 0:
            direction = direction.normalize()*self.stats.mass/10
            self.apply_force_to_object(direction)


    def attack(self, target_rect: pygame.Rect):
        # Update character state to attacking
        self.current_action = CharacterActions.ATTACKING
        self.attack_direction = pygame.Vector2(target_rect.x-self.rect.x, target_rect.y-self.rect.y)


@dataclass
class DamageAction:
    origin: Character
    target: Character # Default value