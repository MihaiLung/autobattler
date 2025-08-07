import sys
import dataclasses
import pygame
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )
pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()

from map_logic.encounter_icon import CircularImageSprite
from tuple_utils import *
from info_window import InformationWindow
from mouse_manager import MouseManager

spr = CircularImageSprite("../assets/goodboy.png", (WIDTH/2, HEIGHT/2))

background = pygame.image.load('../assets/fantasia_mappia.png')
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))


active_window = None
mouse_manager = MouseManager()

def highlight_hover():
    if spr.rect.collidepoint(pygame.mouse.get_pos()):
        if not spr.is_highlighted:
            spr.is_highlighted = True
            spr.refresh_image(True)
    else:
        if spr.is_highlighted:
            spr.is_highlighted = False
            spr.refresh_image(False)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if spr.rect.collidepoint(pygame.mouse.get_pos()):


        if event.type == pygame.MOUSEBUTTONUP:
            mouse_manager.reset_clicked_object()


    screen.blit(background, (0, 0))
    mouse_manager.update()

    if active_window:
        active_window.draw(screen)
    highlight_hover()
    spr.draw(screen)

    pygame.display.update()
    clock.tick(120)
