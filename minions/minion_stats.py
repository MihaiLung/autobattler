from minions.minion_base_class import MinionStats
import pygame
import os

from settings import SCALE

sword_image = pygame.image.load('assets/sword.png').convert_alpha()
sword_image = pygame.transform.scale(sword_image, (100*SCALE,100*SCALE))

axe_image = pygame.image.load('assets/axe.png').convert_alpha()
axe_image = pygame.transform.scale(axe_image, (100*SCALE,100*SCALE))

current_dir = os.path.dirname(__file__)
get_image_path = lambda im_name: os.path.join(current_dir, '..', 'assets', im_name)


elf_stats = MinionStats(
    size=100,
    health=30,
    armour=2,
    attack=5,
    attack_speed=2,
    splash_limit=1,
    movement_speed=3,
    mass=100,
    image_loc="assets/elf.png",
    weapon=sword_image,
)

orc_stats = MinionStats(
    size=150,
    health=100,
    armour=1,
    attack=40,
    attack_speed=3,
    splash_limit=1,
    movement_speed=1,
    mass=400,
    image_loc="assets/orc.png",
    weapon=pygame.transform.scale(axe_image,(200*SCALE,200*SCALE)),
)