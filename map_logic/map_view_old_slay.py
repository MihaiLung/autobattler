import sys

import pygame
from settings import *

from tuple_utils import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )
pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()

background = pygame.image.load('../assets/fantasia_mappia.png')
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

rects = {
    "mountain": pygame.Rect(0,0, WIDTH*2/3, HEIGHT/3),
    "swamp": pygame.Rect(0, HEIGHT/3, WIDTH*2/3, HEIGHT/3),
    "forest": pygame.Rect(0, HEIGHT*2/3, WIDTH*2/3, HEIGHT/3),
    "farmland": pygame.Rect(WIDTH*2/3, 0, WIDTH*1/3, HEIGHT),
}



def highlight_hover_rect(rects):
    for key in rects:
        rect = rects[key]
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, pygame.Color("#ff0000"), rect, 10)

class Building():
    def __init__(self, rect):
        self.rect = rect

class ActiveWindow():
    def __init__(self, name):
        self.name = name
        self.rect = pygame.Rect(WIDTH*2/3-50, 50, WIDTH/3, HEIGHT-100)
        self.font = pygame.font.SysFont('timesnewroman', 30)
        self.title = self.font.render(self.name.title(), True, "black")

        self.compile()

    def compile(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((235, 213, 179))
        # pygame.draw.rect(self.image, 'white', self.rect)
        title_rect = self.title.get_rect()
        title_rect.midtop = (self.rect.width/2, 0)
        self.image.blit(self.title, title_rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class MouseManager():
    def __init__(self):
        self.active_window = None
        self.start_mouse_pos = None
        self.start_rect = None

    def register_clicked_object(self, window: ActiveWindow, mouse_pos):
        self.active_window = window
        self.start_mouse_pos = mouse_pos
        self.start_rect = window.rect.copy()

    def reset_clicked_object(self):
        self.active_window = None
        self.start_mouse_pos = None

    def get_current_mouse_offset(self):
        return tdiff(pygame.mouse.get_pos(), self.start_mouse_pos)

    def update(self):
        if self.active_window:
            self.active_window.rect.topleft = tadd(self.start_rect.topleft, self.get_current_mouse_offset())



active_window = None
mouse_manager = MouseManager()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if active_window is not None:
                    if active_window.rect.collidepoint(pygame.mouse.get_pos()):
                        mouse_manager.register_clicked_object(active_window, pygame.mouse.get_pos())
                    else:
                        active_window = None
                        mouse_manager.reset_clicked_object()

                else:
                    for map_area_name in rects:
                        rect = rects[map_area_name]
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            active_window = ActiveWindow(map_area_name)
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_manager.reset_clicked_object()


    screen.blit(background, (0, 0))
    mouse_manager.update()

    if active_window:
        active_window.draw(screen)
    else:
        highlight_hover_rect(rects)

    pygame.display.update()
    clock.tick(120)
