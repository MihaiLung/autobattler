import enum

import pygame
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from sys import exit
from user_interface import UIButtons
from game_logic import resolve_collisions, update_group_states
from character import Character
from minions.minion_stats import elf_stats, orc_stats
from typing import Optional

from utils import *


pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()


camera = pygame.sprite.Group()

def get_closest_target(s, target_group):
    return min(target_group,
                        key=lambda t: (s.rect.centerx - t.rect.centerx) ** 2 + (s.rect.centery - t.rect.centery) ** 2)

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

orc_group = CharacterGroup()
elf_group = CharacterGroup()
all_group = CharacterGroup()

attack_animations = pygame.sprite.Group()

num_orcs = 20
num_elfs = 100
proto_orc = Character(orc_stats)
proto_elf = Character(elf_stats)

for _ in range(random.randint(num_orcs//2,num_orcs)):
    new_orc = proto_orc.copy()
    orc_group.add(new_orc)
    all_group.add(new_orc)
for _ in range(random.randint(num_elfs//2,num_elfs)):
    new_elf = proto_elf.copy()
    elf_group.add(new_elf)
    all_group.add(new_elf)


orc_group.set_targets(elf_group)
elf_group.set_targets(orc_group)

refresh_targets_timer = 0

ui = UIButtons()
ui.create_button_for_creature_summon(proto_orc)
ui.create_button_for_creature_summon(proto_elf)
ui.compile_ui_buttons()


class MouseStates(enum.Enum):
    EMPTY="empty"
    HOLDS_CHARACTER="holding"
    SPAWNING="spawning"


class MouseManager:
    SPAWN_COOLDOWN = 20

    def __init__(self):
        self.state = MouseStates.EMPTY
        self.character: Optional[Character] = None
        self.spawn_timer = 0

    def click(self, character: Optional[Character] = None):
        # If pressed outside UI:
        if character is None:
            # If no
            if self.character is not None:
                # Reset
                self.state = MouseStates.SPAWNING
                # self.character = None

        # If pressed in UI
        else:
            self.state = MouseStates.HOLDS_CHARACTER
            self.character = character.copy()


    def unclick(self):
        self.spawn_timer = 0
        if self.state == MouseStates.SPAWNING:
            self.character = None
            self.state = MouseStates.EMPTY
            # if self.character is None:
            #     self.state = MouseStates.EMPTY
            # else:
            #     self.state = MouseStates.HOLDS_CHARACTER

    def hover(self, screen: pygame.Surface):
        if self.character is not None:
            self.character.draw(screen, pygame.mouse.get_pos())
        if self.state == MouseStates.SPAWNING:
            if self.spawn_timer == 0:
                new_char = self.character.copy()
                new_char.position = pygame.Vector2(pygame.mouse.get_pos())
                side = elf_group if "elf" in new_char.stats.image_loc else orc_group
                side.add(new_char)
                all_group.add(new_char)
                self.spawn_timer = MouseManager.SPAWN_COOLDOWN
            self.spawn_timer -= 1


mouse_manager = MouseManager()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                if ui.rect.collidepoint(mouse_pos):
                    relative_mouse_loc = pygame.Vector2(mouse_pos)-pygame.Vector2(ui.rect.topleft)
                    button_index = int(relative_mouse_loc[0]//(UI_BUTTON_SIZE*SCALE))
                    mouse_manager.click(ui.buttons[button_index].creature)
                else:
                    mouse_manager.click()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_manager.unclick()



    refresh_targets_timer += 1
    if refresh_targets_timer>120:
        refresh_targets_timer = 0
        orc_group.set_targets(elf_group)
        elf_group.set_targets(orc_group)

    background = pygame.image.load("assets/background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT) )
    screen.blit(background, (0, 0))

    # Runs the update command on everyone, which gets move intentions, and resolves damage
    # update_all_character_states(orc_group, elf_group)
    update_group_states(orc_group, elf_group, attack_animations)
    update_group_states(elf_group, orc_group, attack_animations)

    # Collision
    # resolve_collisions(orc_group)
    # resolve_collisions(elf_group)
    resolve_collisions(all_group)

    orc_group.update_rect_position()
    elf_group.update_rect_position()

    orc_group.draw(screen)
    elf_group.draw(screen)

    attack_animations.update()
    attack_animations.draw(screen)

    ui.draw(screen)
    mouse_manager.hover(screen)



    pygame.display.update()
    clock.tick(120)
