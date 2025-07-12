from settings import *
from game_logic import update_group_states, resolve_collisions
from character import CharacterGroup
# from user_interface import UIButtons

class BattleManager:
    def __init__(self, allied_group, enemy_group, screen):
        self.allied_group = allied_group
        self.enemy_group = enemy_group
        self.collision_group = CharacterGroup()
        for sprite in self.allied_group.sprites()+self.enemy_group.sprites():
            self.collision_group.add(sprite)

        self.collision_group = pygame.sprite.Group()

        self.screen = screen
        self.refresh_targets_timer = 0
        background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        self.attack_animations = pygame.sprite.Group()


    def update(self):
        self.refresh_targets_timer += 1
        if self.refresh_targets_timer > 120:
            refresh_targets_timer = 0
            self.enemy_group.set_targets(self.allied_group)
            self.allied_group.set_targets(self.enemy_group)

        self.screen.blit(self.background, (0, 0))

        # Runs the update command on everyone, which gets move intentions, and resolves damage
        update_group_states(self.enemy_group, self.allied_group, self.attack_animations)
        update_group_states(self.allied_group, self.enemy_group, self.attack_animations)

        # Collision
        resolve_collisions(self.collision_group)

        self.enemy_group.update_rect_position()
        self.allied_group.update_rect_position()

        self.enemy_group.draw(self.screen)
        self.allied_group.draw(self.screen)

        self.attack_animations.update()
        self.attack_animations.draw(self.screen)

        # ui.draw(self.screen)
        # mouse_manager.hover(self.screen)
