import pygame

from settings import WIDTH, HEIGHT


class Fireball(pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, target: pygame.Vector2) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((100, 100))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, 'orange', (50, 50), 30)
        self.rect = self.image.get_rect()
        self.position = position
        self.direction = (target-position).normalize()
        self.speed = 15
        self.level = 3
        self.lifetime = 60
        # print("BONHJOUR!!!")

    def update_rect(self):
        self.rect.center = int(self.position[0]), int(self.position[1])

    def update(self):
        self.position += self.direction * self.speed
        self.update_rect()
        is_out_of_bounds = (
            (self.rect.left < 0) or
            (self.rect.right>WIDTH) or
            (self.rect.top < 0) or
            (self.rect.bottom > HEIGHT)
        )
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

