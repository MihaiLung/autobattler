import pygame
import pygame.image
import pygame.sprite
import pygame.transform


class Building(pygame.sprite.Sprite):
    def __init__(self, init=True):
        pygame.sprite.Sprite.__init__(self)
        if init:
            self.image = pygame.image.load("../assets/magical_conveyor.png")
            self.image = pygame.transform.scale(self.image, (100,100))
            self.rect = self.image.get_rect()
        else:
            self.image = None
            self.rect = None

    @property
    def image_raw(self):
        return self.image.copy()

    def load_image(self):
        pass

    def copy(self):
        new_conveyor = Building(False)
        new_conveyor.image = self.image.copy()
        new_conveyor.rect = self.rect.copy()
        return new_conveyor
