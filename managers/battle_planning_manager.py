from managers.mouse_manager import MouseManager
from settings import *
from battle.character import Character, CharacterGroup
from user_interface import CreatureSummonUI, Button
from typing import List


class BattlePlanningManager:
    def __init__(
            self,
            allied_character_options: List[Character],
            enemy_character_options: List[Character],
            screen: pygame.Surface,
    ):


        self.allied_group = CharacterGroup()
        self.enemy_group = CharacterGroup()

        self.ui_allied = CreatureSummonUI(self.allied_group)
        for creature in allied_character_options:
            self.ui_allied.create_button_for_creature_summon(creature)

        self.ui_enemy = CreatureSummonUI(self.enemy_group)
        for creature in enemy_character_options:
            self.ui_enemy.create_button_for_creature_summon(creature)

        self.all_ui_instances = [self.ui_allied, self.ui_enemy]
        for ui in self.all_ui_instances:
            ui.compile_ui_buttons()
        self.ui_allied.rect.left = 0
        self.ui_enemy.rect.right = WIDTH

        background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))

        self.screen = screen
        self.mouse_manager = MouseManager()
        self.planning_done_button = Button(
            text="START!",
            rect=pygame.Rect(WIDTH / 2 - 100, 20, 200, 70),
            button_press_event=pygame.event.Event(GameEvents.BattlePlanningDone.value)
        )


    def update(self, pygame_events):
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_pos = pygame.mouse.get_pos()

                    clicked = False
                    for ui in self.all_ui_instances:
                        if ui.rect.collidepoint(mouse_pos):
                            relative_mouse_loc = pygame.Vector2(mouse_pos) - pygame.Vector2(ui.rect.topleft)
                            button_index = int(relative_mouse_loc[0] // (UI_BUTTON_SIZE * SCALE))
                            self.mouse_manager.click(ui.buttons[button_index].creature, ui.team)
                            clicked = True
                    if self.planning_done_button.rect.collidepoint(mouse_pos):
                        self.planning_done_button.button_press()
                        clicked = True
                    if not clicked:
                        self.mouse_manager.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_manager.unclick()

        for ui in self.all_ui_instances:
            ui.draw(self.screen)

        # self.mouse_manager.hover(self.screen)
        self.draw()

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        self.enemy_group.draw(self.screen)
        self.allied_group.draw(self.screen)

        self.ui_allied.draw(self.screen)
        self.ui_enemy.draw(self.screen)

        self.mouse_manager.hover(self.screen)
        self.planning_done_button.draw(self.screen)


