from battle_logic.character_settings.minion_base_class import MinionStats
from battle_logic.character_settings.minion_stats import orc_stats
from battle_logic.managers.battle_planning_mouse_manager import MouseManager
from settings import *
from battle_logic.character import Character, CharacterGroup
from ui.sprite_summon_menu import SpriteSummonUI
from ui.buttons import Button
from ui.resource_topbar import ResourceTopBar, ResourceTracker
from typing import List, Tuple



enemies_config = {
    Character(orc_stats): 10
}

def generate_character_formation(
        character: Character,
        num_characters,
        max_per_row=8,
        gap_multiplier=1.3,
        enemy=True
):
    diameter = character.diameter
    num_rows = num_characters // max_per_row + 1
    x_coord_start = WIDTH/2-diameter*gap_multiplier * max_per_row / 2
    y_coord = HEIGHT*0.3
    formation = []

    for row in range(num_rows-1):
        x_coord = x_coord_start
        for i in range(max_per_row):
            new_character = character.copy()
            new_character.set_position_center((x_coord, y_coord))
            x_coord += diameter*gap_multiplier
            formation.append(new_character)
        y_coord -= diameter*gap_multiplier

    num_last_row = num_characters-(num_rows-1)*max_per_row
    x_coord = WIDTH/2-diameter*gap_multiplier * num_last_row / 2
    for i in range(num_last_row):
        new_character = character.copy()
        new_character.set_position_center((x_coord, y_coord))
        x_coord += diameter * gap_multiplier
        formation.append(new_character)


    return formation



class BattlePlanningManager:
    def __init__(
            self,
            allied_character_config: List[MinionStats],
            enemies_config: ENEMIES_CONFIG_DTYPE,
            screen: pygame.Surface,
    ):

        self.allied_group = CharacterGroup()
        self.enemy_group = CharacterGroup()
        enemies = []

        self.ui_allied = SpriteSummonUI(self.allied_group)
        for creature_stats in allied_character_config:
            self.ui_allied.create_button_for_sprite_generation(Character(creature_stats, self.allied_group, self.enemy_group))

        for (enemy_stats, num_enemies) in enemies_config:
            enemies.extend(generate_character_formation(Character(enemy_stats, self.enemy_group, self.allied_group), num_enemies))
            enemies[-1].group = self.enemy_group
        self.enemy_group.add(enemies)


        self.all_ui_instances = [self.ui_allied]
        for ui in self.all_ui_instances:
            ui.compile_ui_buttons()

        background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))

        self.screen = screen
        self.planning_done_button = Button(
            text="START!",
            rect=pygame.Rect(WIDTH / 2 - 100, 70, 200, 70),
            button_press_event=pygame.event.Event(GameEvents.BattlePlanningDone.value)
        )

        resources = [
            ResourceTracker("Elfs", "elf.png", 60)
        ]
        self.resource_top_bar = ResourceTopBar(resources)
        self.mouse_manager = MouseManager(self.resource_top_bar)


    def update(self, pygame_events):
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_pos = pygame.mouse.get_pos()

                    clicked = False
                    for ui in self.all_ui_instances:
                        if ui.rect.collidepoint(mouse_pos):
                            self.mouse_manager.click(ui.get_button_at_mouse_position().proto_sprite, ui.team)
                            clicked = True
                    if self.planning_done_button.rect.collidepoint(mouse_pos):
                        if len(self.allied_group.sprites())>0 and len(self.enemy_group.sprites())>0:
                            self.planning_done_button.button_press()
                        clicked = True
                    if not clicked:
                        self.mouse_manager.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_manager.unclick()

        self.draw()

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        self.enemy_group.draw(self.screen)
        self.allied_group.draw(self.screen)

        self.ui_allied.draw(self.screen)

        self.mouse_manager.hover(self.screen)
        self.planning_done_button.draw(self.screen)
        self.resource_top_bar.draw(self.screen)


