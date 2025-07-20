import pygame
from typing import Optional

class Settlement(pygame.sprite.Sprite):
    def __init__(self, image_loc=Optional[str]):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_loc).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (250, 250))
        self.rect = self.image.get_rect()

    def copy(self):
        settlement_copy = Settlement()
        settlement_copy.image = self.image
        settlement_copy.rect = self.rect

orc_settlement = Settlement("../assets/orc_settlement.png")
elf_settlement = Settlement("../assets/elf_settlement.png")

class Shadow(pygame.sprite.Sprite):
    SHADOW_COLOR = (0, 0, 0, 100)
    def __init__(self, settlement: Settlement):
        pygame.sprite.Sprite.__init__(self)
        self.image = settlement.image.copy()
        self.image.fill(Shadow.SHADOW_COLOR)
        self.rect = settlement.rect.copy().move(3,-3)