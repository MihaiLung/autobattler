import pygame
from settings import *

class InformationWindow(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
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
        title_rect.midtop = (int(self.rect.width/2), 0)
        self.image.blit(self.title, title_rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class InformationWindowEntry(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class EnemiesCount(InformationWindowEntry):
    def __init__(self, enemies: pygame.sprite.Group):
        super().__init__()
