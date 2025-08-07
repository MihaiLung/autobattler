import pygame

from settings import WIDTH, HEIGHT, CampaignDisplayZ


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("../assets/pc.png").convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.image = pygame.transform.scale(self.image, (100,100))
        self.position = pygame.Vector2(0,0)
        self.rect = self.image.get_rect()
        self.update_rect()

        self.speed = 15
        self.facing_right = True
        self.level = CampaignDisplayZ.player.value


    def update_rect(self):
        self.rect.center = int(self.position[0]), int(self.position[1])

    def get_movement(self):
        x, y = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_s]:
            y += 1

        vec = pygame.Vector2(x, y)
        if vec.magnitude() > 0:
            vec.normalize_ip()
        return vec*self.speed

    def update(self):
        movement = self.get_movement()
        self.position += movement
        if ((movement[0]<0) and (self.facing_right)) or ((movement[0]>0) and (not self.facing_right)):
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = not self.facing_right
        self.update_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
