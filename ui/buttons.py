import pygame


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
