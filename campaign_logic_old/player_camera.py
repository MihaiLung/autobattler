import pygame

# from campaign_logic.campaign_ui import CreatureSummonUI
from campaign_logic.powah import Fireball
from settings import WIDTH, HEIGHT


class PlayerCamera(pygame.sprite.Group):
    def __init__(self, player):
        pygame.sprite.Group.__init__(self)
        self.player = player

    @property
    def offset(self):
        return -self.player.position#+pygame.Vector2(WIDTH/2, HEIGHT/2)

    @property
    def integer_offset(self):
        return int(self.offset.x), int(self.offset.y)

    def sorted_sprites(self):
        return sorted(self.sprites(), key=lambda x: x.level, reverse=False)

    def centered_draw(self, screen):
        for sprite in self.sorted_sprites():
            # if sprite is self.player:
            if sprite is self.player:
                sprite.rect.center = (int(WIDTH / 2), int(HEIGHT / 2))
            else:
                if isinstance(sprite, pygame.sprite.Group):
                    print("HENLO1")
                    for s in sprite:
                        print("HENLO2")
                        rect_offset = s.rect.move(self.integer_offset)
                        screen.blit(s.image, rect_offset)
                elif isinstance(sprite, pygame.sprite.Sprite):
                    rect_offset = sprite.rect.move(self.integer_offset)
                    screen.blit(sprite.image, rect_offset)
