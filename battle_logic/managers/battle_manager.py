from settings import *
from battle_logic.logic.game_logic import update_group_states, resolve_collisions
from battle_logic.battle.character import CharacterGroup
# from user_interface import UIButtons

class AttackAnimations(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface: pygame.Surface):
        for sprite in self.sprites():
            sprite.draw(surface)

class BattleManager:
    def __init__(self, allied_group, enemy_group, screen):
        self.allied_group = allied_group
        self.enemy_group = enemy_group
        self.collision_group = CharacterGroup()
        for sprite in self.allied_group.sprites()+self.enemy_group.sprites():
            self.collision_group.add(sprite)

        # self.collision_group = pygame.sprite.Group()

        self.screen = screen
        self.refresh_targets_timer = 120
        background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        self.attack_animations = AttackAnimations()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.enemy_group.draw(self.screen)
        self.allied_group.draw(self.screen)

        # font = pygame.font.SysFont("comicsans", 20)
        # for sprite in self.collision_group.sprites():
        #     text = font.render(str(round(sprite.collision_resolution_priority,0)), 0, "black")
        #     self.screen.blit(text, (sprite.rect.x, sprite.rect.y))

        # for sprite in self.collision_group.sprites():
        #     pygame.draw.circle(
        #         self.screen,
        #         "red",
        #         (int(sprite.central_position_for_collision[0]), int(sprite.central_position_for_collision[1])),
        #         int(sprite.radius*1.2/2),
        #         width=int(sprite.radius*0.2)
        #     )

        self.attack_animations.draw(self.screen)


    def update(self):

        # try:
            self.refresh_targets_timer += 1
            if (self.refresh_targets_timer > 120):
                refresh_targets_timer = 0
                self.enemy_group.set_targets(self.allied_group)
                self.allied_group.set_targets(self.enemy_group)

            # Runs the update command on everyone, which gets move intentions, and resolves damage
            update_group_states(self.enemy_group, self.allied_group, self.attack_animations)
            update_group_states(self.allied_group, self.enemy_group, self.attack_animations)

            # Collision
            resolve_collisions(self.allied_group, self.enemy_group)

            self.enemy_group.update_rect_position()
            self.allied_group.update_rect_position()
            self.attack_animations.update()

            self.draw()

            if min(len(self.enemy_group), len(self.allied_group)) == 0:
                pygame.event.post(pygame.event.Event(GameEvents.BattleDone.value))

        # except ValueError:
        #     pygame.event.post(pygame.event.Event(GameEvents.BattleDone.value))




        # if min(
        #         len(self.allied_group.sprites()),
        #         len(self.enemy_group.sprites())
        # )==0:
        #     pygame.event.post(pygame.event.Event(GameEvents.BattleDone.value))
        #     return None
        #
        # self.refresh_targets_timer += 1
        # if self.refresh_targets_timer > 120:
        #     refresh_targets_timer = 0
        #     self.enemy_group.set_targets(self.allied_group)
        #     self.allied_group.set_targets(self.enemy_group)
        #
        # self.screen.blit(self.background, (0, 0))
        #
        # # Runs the update command on everyone, which gets move intentions, and resolves damage
        # update_group_states(self.enemy_group, self.allied_group, self.attack_animations)
        # update_group_states(self.allied_group, self.enemy_group, self.attack_animations)
        #
        # # Collision
        # resolve_collisions(self.collision_group)
        #
        # self.enemy_group.update_rect_position()
        # self.allied_group.update_rect_position()
        #
        # self.enemy_group.draw(self.screen)
        # self.allied_group.draw(self.screen)
        #
        # self.attack_animations.update()
        # self.attack_animations.draw(self.screen)



