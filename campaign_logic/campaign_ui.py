from settings import *
from battle_logic.battle.character import Character, CharacterGroup
from battle_logic.character_settings.minion_stats import *
from settings import WIDTH


class BuildingButton(pygame.sprite.Sprite):
    def __init__(self, building):
        pygame.sprite.Sprite.__init__(self)
        self.building = building.copy()
        self.building_icon = building.copy()
        self.building_icon.radius = UI_BUTTON_SIZE*SCALE

        self.image = pygame.transform.smoothscale(self.building_icon.image, (UI_BUTTON_SIZE*SCALE, UI_BUTTON_SIZE*SCALE))
        self.rect = self.image.get_rect()

    def build_building(self, position: pygame.Vector2):
        new_building = self.building.copy()
        new_building.position = position
        return new_building


class BuildingUI(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.buttons = []
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()


    def _create_button_for_building(self, building):
        self.buttons.append(BuildingButton(building))

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

