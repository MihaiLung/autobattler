import enum

import pygame
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from sys import exit
from battle_manager import BattleManager
from user_interface import UIButtons
from game_logic import resolve_collisions, update_group_states
from character import Character, CharacterGroup
from minions.minion_stats import elf_stats, orc_stats
from mouse_manager import MouseManager

from utils import *


pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()


camera = pygame.sprite.Group()

# def get_closest_target(s, target_group):
#     return min(target_group,
#                         key=lambda t: (s.rect.centerx - t.rect.centerx) ** 2 + (s.rect.centery - t.rect.centery) ** 2)

# class CharacterGroup(pygame.sprite.Group):
#     def __init__(self):
#         super().__init__()
#
#     def set_targets(self, target_group):
#         pairings = {}
#         for s in self:
#             # Find t in target_group with min distance to s
#             s.set_target(get_closest_target(s, target_group))
#
#     def update_rect_position(self):
#         for s in self:
#             s.update_rect_position()

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



mouse_manager = MouseManager()

battle_manager = BattleManager(elf_group, orc_group, screen)


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



    battle_manager.update()

    ui.draw(screen)
    mouse_manager.hover(screen, battle_manager.allied_group, battle_manager.enemy_group, battle_manager.collision_group)



    pygame.display.update()
    clock.tick(120)
