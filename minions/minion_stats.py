import sys

from minions.minion_base_class import MinionStats
import pygame
import os

current_dir = os.path.dirname(__file__)
get_image_path = lambda im_name: os.path.join(current_dir, '..', 'assets', im_name)


elf_stats = MinionStats(
    size=100,
    health=30,
    armour=2,
    attack=5,
    attack_speed=2,
    movement_speed=10,
    mass=100,
    image_loc="assets/elf.png",
)

orc_stats = MinionStats(
    size=150,
    health=110,
    armour=1,
    attack=15,
    attack_speed=3,
    movement_speed=1,
    mass=180,
    image_loc="assets/orc.png",
)