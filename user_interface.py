import pygame

from settings import *
from battle.character import Character, CharacterGroup
from character_settings.minion_stats import *
from settings import WIDTH
from typing import Tuple, Callable


class CreatureSummonButton(pygame.sprite.Sprite):
    def __init__(self, creature: Character):
        pygame.sprite.Sprite.__init__(self)
        self.creature = creature.copy()
        self.creature_icon = creature.copy()
        self.creature_icon.radius = UI_BUTTON_SIZE*SCALE
        self.creature_icon.load_image()

        self.image = pygame.transform.smoothscale(self.creature_icon.image_raw, (UI_BUTTON_SIZE*SCALE, UI_BUTTON_SIZE*SCALE))
        self.rect = self.image.get_rect()
        print(self.rect)

    def summon_creature(self, position: pygame.Vector2, group: pygame.sprite.Group):
        new_creature = self.creature.copy()
        new_creature.position = position
        group.add(new_creature)


class CreatureSummonUI(pygame.sprite.Sprite):
    def __init__(self, team: CharacterGroup):
        pygame.sprite.Sprite.__init__(self)
        self.buttons = []
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        self.team = team


    def create_button_for_creature_summon(self, creature):
        self.buttons.append(CreatureSummonButton(creature))

    def compile_ui_buttons(self):
        left_offset = 0
        width = UI_BUTTON_SIZE*SCALE*len(self.buttons)
        self.image = pygame.Surface((width, UI_BUTTON_SIZE*SCALE))
        self.image.fill('white')
        for button in self.buttons:
            print(button)
            button.rect.left += left_offset
            self.image.blit(button.image, button.rect)
            left_offset += button.rect.width
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect.centerx = WIDTH//2
        print(self.rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Button(pygame.sprite.Sprite):
    DEFAULT_COLOR = (255, 255, 255)
    HOVER_COLOR = (0, 200, 0)
    BLACK = (0, 0, 0)

    def __init__(self, text: str, rect: pygame.Rect, button_press_event: pygame.event.Event):
        pygame.sprite.Sprite.__init__(self)
        self.pressed = False
        self.font = pygame.font.Font(None, 40)
        self.text = text
        self.rect = rect
        self.button_press_event = button_press_event

    def draw(self, screen: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        is_mouse_over_button = self.rect.collidepoint(mouse_pos)

        current_color = Button.HOVER_COLOR if is_mouse_over_button else Button.DEFAULT_COLOR
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        text_surface = self.font.render("DONE", True, Button.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def button_press(self):
        pygame.event.post(self.button_press_event)

