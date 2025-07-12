import pygame
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from sys import exit

from game_logic import resolve_collisions, update_group_states
from character import Character, DamageAction, CharacterActions
from minions.minion_stats import elf_stats, orc_stats

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

num_orcs = 50
num_elfs = 300
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


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


    pygame.display.update()
    clock.tick(120)
