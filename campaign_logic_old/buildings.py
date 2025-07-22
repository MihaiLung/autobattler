import pygame
import pygame.image
import pygame.sprite
import pygame.transform
from settings import *


class Building(pygame.sprite.Sprite):
    def __init__(self, size=None):
        pygame.sprite.Sprite.__init__(self)
        if not size:
            size = CAMPAIGN_TILE_SIZE*SCALE
        self.load_image(size)

    def load_image(self, size):
        self.image = pygame.image.load("../assets/magical_conveyor.png")
        self.size = size
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect()


    @property
    def image_raw(self):
        return self.image.copy()

    def copy(self):
        new_conveyor = Building(False)
        new_conveyor.image = self.image.copy()
        new_conveyor.rect = self.rect.copy()
        return new_conveyor

    def draw(self, screen, topleft):
        draw_rect = self.rect.copy()
        draw_rect.topleft = topleft
        screen.blit(self.image, draw_rect)