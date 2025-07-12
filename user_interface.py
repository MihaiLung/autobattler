from settings import *
from character import Character
from minions.minion_stats import *


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


class UIButtons(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.buttons = []
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()


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


