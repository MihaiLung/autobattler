import random
from typing import List, Tuple

import pygame


class DestroySprite:
    def __init__(self, image: pygame.Surface, rect: pygame.Rect, angle_range: Tuple[int, int]):
        self.image = image
        self.image = pygame.transform.scale(self.image, (200,200))
        # self.rect = self.image.get_rect()
        self.rect = rect
        self.slices: List['DestroySprite'] = []
        self.angle_range = angle_range

    @staticmethod
    def triangle():
        height = random.randint(5,10)
        base = random.randint(5, 10)
        alpha = random.randint(0, 120)

    def slice(self):
        angle = random.randint(self.angle_range[0], self.angle_range[1])
        rotated_image = pygame.transform.rotate(self.image, angle)
        left_width = random.randint(int(self.rect.width*0.1), int(self.rect.width*0.9))
        subrect_left = pygame.Rect(0, 0, left_width, self.rect.height)
        subsurface_left = rotated_image.subsurface(subrect_left)
        sprite_left = DestroySprite(pygame.transform.rotate(subsurface_left, -angle), self.rect)

        subrect_right = pygame.Rect(left_width, 0, self.rect.width-left_width, self.rect.height)
        subsurface_right = rotated_image.subsurface(subrect_right)
        sprite_right = DestroySprite(pygame.transform.rotate(subsurface_right, -angle), self.rect)

        return [sprite_left,sprite_right]



spr = DestroySprite(image=pygame.image.load("../assets/orc.png"), rect=pygame.Rect(0, 0, 200, 200), angle_range=(0, 360))


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Pygame Explosion")

clock = pygame.time.Clock()
FPS = 60

sprites = [spr]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            new_sprites = []
            for s in sprites:
                new_sprites.extend(s.slice())
            sprites = new_sprites

    screen.fill((30, 30, 30)) # Dark background
    for s in sprites:
        screen.blit(s.image, s.rect)

    pygame.display.flip()
    clock.tick(FPS)