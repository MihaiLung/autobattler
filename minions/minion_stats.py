import sys

from minions.minion_base_class import MinionStats
import pygame
import os

current_dir = os.path.dirname(__file__)
get_image_path = lambda im_name: os.path.join(current_dir, '..', 'assets', im_name)


elf_stats = MinionStats(
    health=30,
    armour=2,
    attack=5,
    attack_speed=2,
    movement_speed=2,
    mass=200,
    image_loc="assets/elf.png",
    is_player_controlled=True
)

orc_stats = MinionStats(
    health=50,
    armour=1,
    attack=4,
    attack_speed=2,
    movement_speed=1,
    mass=100,
    image_loc="assets/orc.png",
    is_player_controlled=False
)