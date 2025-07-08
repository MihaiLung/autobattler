import pygame
from sys import exit
from settings import *
from character import Character, DamageAction
from minions.minion_stats import elf_stats, orc_stats

pygame.init()
pygame.display.set_caption("World of VAVAVAVA")
screen = pygame.display.set_mode((WIDTH, HEIGHT) )
clock = pygame.time.Clock()


camera = pygame.sprite.Group()

orc = Character(orc_stats, camera)
elf = Character(elf_stats, camera)

orc.set_target_rect(elf)
elf.set_target_rect(orc)




while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    background = pygame.image.load("assets/background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT) )
    screen.blit(background, (0, 0))


    for char in (orc, elf):
        game_action = char.update()
        if type(game_action)==DamageAction:
            # Resolve damage
            char.damage(char.target)
            char.target.update_image()


    camera.draw(screen)


    pygame.display.update()
    clock.tick(120)
