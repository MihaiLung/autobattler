from settings import *
from battle_logic.character import CharacterGroup
from settings import WIDTH
from typing import Optional

from utils import get_asset_path


class SelectSpriteButton(pygame.sprite.Sprite):
    def __init__(self, proto_sprite):
        pygame.sprite.Sprite.__init__(self)

        # Create a copy of the sprite instance, to be used as the parent for further instances
        self.proto_sprite = proto_sprite.copy()

        # Initialize the UI button by reading in the image from scratch (ensure good resolution)
        self.image = pygame.image.load(get_asset_path(proto_sprite.image_path)).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (UI_BUTTON_SIZE, UI_BUTTON_SIZE))
        self.rect = self.image.get_rect()


class SpriteSummonUI(pygame.sprite.Sprite):
    def __init__(self, team: Optional[CharacterGroup] = None):
        pygame.sprite.Sprite.__init__(self)
        self.buttons = []
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        self.team = team

    def get_button_index_at_mouse_position(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            relative_mouse_x_loc = mouse_pos[0] - self.rect.left
            return int(relative_mouse_x_loc // UI_BUTTON_SIZE)
        else:
            return None

    def get_button_at_mouse_position(self):
        return self.buttons[self.get_button_index_at_mouse_position()]

    def create_button_for_sprite_generation(self, sprite):
        self.buttons.append(SelectSpriteButton(sprite))

    def compile_ui_buttons(self):
        """
        Once all UI buttons have been registered, call this to actually render the AI
        :return:
        """
        left_offset = 0
        width = UI_BUTTON_SIZE*len(self.buttons)

        # Fill out the UI with buttons
        self.image = pygame.Surface((width, UI_BUTTON_SIZE))
        self.image.fill('white')
        for button in self.buttons:
            print(button)
            button.rect.left += left_offset
            self.image.blit(button.image, button.rect)
            left_offset += button.rect.width

        # Align the UI to the bottom-center (this can be moved manually)
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect.centerx = WIDTH//2

    def draw(self, screen):
        screen.blit(self.image, self.rect)


