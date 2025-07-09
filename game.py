import pygame
from sys import exit
from settings import *
from character import Character, DamageAction, CharacterActions
from minions.minion_stats import elf_stats, orc_stats
import random


pygame.init()
pygame.display.set_caption("World of VAVAVAVA")
screen = pygame.display.set_mode((WIDTH, HEIGHT) )
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

orc_group = CharacterGroup()
elf_group = CharacterGroup()

num_orcs = 30
num_elfs = 100

for _ in range(random.randint(num_orcs//2,num_orcs)):
    orc_group.add(Character(orc_stats, camera))
for _ in range(random.randint(num_elfs//2,num_elfs)):
    elf_group.add(Character(elf_stats, camera))


orc_group.set_targets(elf_group)
elf_group.set_targets(orc_group)

refresh_targets_timer = 0
while True:

    refresh_targets_timer += 1
    if refresh_targets_timer>120:
        refresh_targets_timer = 0
        orc_group.set_targets(elf_group)
        elf_group.set_targets(orc_group)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    background = pygame.image.load("assets/background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT) )
    screen.blit(background, (0, 0))


    need_refresh_targets = False
    for char in orc_group:
        game_action = char.update()
        if type(game_action) == DamageAction:
            # Resolve damage
            char.damage(char.target)
            char.target.update_image()

        elif game_action == "dead":
            need_refresh_targets = True
    if need_refresh_targets:
        elf_group.set_targets(orc_group)

    need_refresh_targets = False
    for char in elf_group:
        game_action = char.update()
        if type(game_action) == DamageAction:
            # Resolve damage
            char.damage(char.target)
            char.target.update_image()

        elif game_action == "dead":
            need_refresh_targets = True
    if need_refresh_targets:
        orc_group.set_targets(elf_group)

        # collision
    all_sprites = orc_group.sprites() + elf_group.sprites()
    if refresh_targets_timer % 2 == 0:

        # assign sprites to quadrants
        d_quadrants = {}
        for sprite in all_sprites:
            quadrant = sprite.get_quadrant()
            if quadrant not in d_quadrants:
                d_quadrants[quadrant] = []
            d_quadrants[quadrant].append(sprite)

        # Quadrant-by-quadrant, resolve conflicts
        for quadrant in d_quadrants:
            # Iterate over each sprite in a given quadrant
            for s in d_quadrants[quadrant]:
                # Iterate over all other sprite it could interact with
                for target in d_quadrants[quadrant]:
                    if s is target:
                        continue
                    else:
                        intersection_rect = s.rect.clip(target.rect)
                        intersection_area = intersection_rect.width * intersection_rect.height
                        # If collision detected -> resolve
                        if intersection_area > 0.01:
                            source_force = s.momentum * s.stats.mass
                            target_force = target.momentum * target.stats.mass
                            # direction = source_force + target_force
                            direction = pygame.Vector2(s.rect.center) - pygame.Vector2(target.rect.center)
                            perpendicular = direction.rotate(90)

                            if (direction.magnitude() > 0.05) and (s.momentum.magnitude() > 0.05):
                                s.apply_force_to_object(direction.normalize() * intersection_area * target.stats.mass / s.stats.mass)
                                # s.momentum = s.momentum.reflect(direction)

    orc_group.draw(screen)
    elf_group.draw(screen)

    pygame.display.update()
    clock.tick(120)
