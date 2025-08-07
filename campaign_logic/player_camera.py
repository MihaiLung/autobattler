import pygame

from battle_logic.logic.utils import vector_to_integer_tuple
# from campaign_logic.campaign_ui import CreatureSummonUI
from campaign_logic.powah import Fireball
from settings import WIDTH, HEIGHT

class PlayerCamera(pygame.sprite.Group):
    SCREEN_CENTER = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    def __init__(self, player):
        pygame.sprite.Group.__init__(self)
        self.player = player

    @property
    def offset(self):
        return self.player.position-pygame.Vector2(WIDTH/2, HEIGHT/2)

    # @property
    # def integer_offset(self):
    #     return int(self.offset.x), int(self.offset.y)

    def sorted_sprites(self):
        return sorted(self.sprites(), key=lambda x: x.level, reverse=False)

    def centered_draw(self, screen):
        for sprite in self.sorted_sprites():
            # if sprite is self.player:
            if sprite is self.player:
                sprite.rect.center = (int(WIDTH / 2), int(HEIGHT / 2))
                screen.blit(sprite.image, sprite.rect)
            else:
                if isinstance(sprite, pygame.sprite.Group):
                    for s in sprite:
                        rect_offset = s.rect.move(vector_to_integer_tuple(-self.offset))
                        screen.blit(s.image, rect_offset)
                elif isinstance(sprite, pygame.sprite.Sprite):
                    rect_offset = sprite.rect.move(vector_to_integer_tuple(-self.offset))
                    screen.blit(sprite.image, rect_offset)
