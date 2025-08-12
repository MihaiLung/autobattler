import pygame

from utils import load_image
from settings import WIDTH
from typing import Tuple

TOPBAR_HEIGHT = 40

class ResourceTracker(pygame.sprite.Sprite):
    FONT = pygame.font.SysFont("timesnewroman", 20)

    def __init__(self, name: str, image_loc: str, amount: int = 0, proposed_reduction: int = 0):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image = load_image(image_loc)
        self.image = pygame.transform.smoothscale(self.image, (TOPBAR_HEIGHT,TOPBAR_HEIGHT))
        # self.image.set_colorkey("black")
        self.rect = self.image.get_rect()

        self.amount = amount
        self.proposed_reduction = proposed_reduction

    def confirm_proposed_reduction(self):
        self.amount = self.amount - self.proposed_reduction
        self.proposed_reduction = 0
        self.refresh_display()

    def refresh_display(self) -> Tuple[pygame.Surface, pygame.Rect]:
        display_image = pygame.Surface((120,TOPBAR_HEIGHT), pygame.SRCALPHA)
        display_image.blit(self.image, (0, 0))
        text_available_amount = ResourceTracker.FONT.render(str(int(self.amount)), True, "black").convert_alpha()
        text_available_amount_rect = text_available_amount.get_rect()
        text_available_amount_rect.centery = int(TOPBAR_HEIGHT/2)
        text_available_amount_rect.left = int(TOPBAR_HEIGHT*1.1)
        display_image.blit(text_available_amount, text_available_amount_rect)

        if self.proposed_reduction > 0:
            text_proposed_reduction = ResourceTracker.FONT.render(f"(-{str(int(self.proposed_reduction))})", True, "red").convert_alpha()
            text_proposed_reduction_rect = text_proposed_reduction.get_rect()
            text_proposed_reduction_rect.centery = int(TOPBAR_HEIGHT/2)
            text_proposed_reduction_rect.left = text_available_amount_rect.right+TOPBAR_HEIGHT*0.1
            display_image.blit(text_proposed_reduction, text_proposed_reduction_rect)


        return display_image, display_image.get_rect()


class ResourceTopBar(pygame.sprite.Sprite):

    def __init__(self, resources):
        pygame.sprite.Sprite.__init__(self)

        self.empty_ui_image = pygame.Surface((WIDTH, TOPBAR_HEIGHT))
        self.empty_ui_image.fill("grey")
        self.margin = 50

        self.resources = resources
        self.compile_ui()

    def compile_ui(self):
        self.image = self.empty_ui_image.copy()
        start = self.margin
        for resource in self.resources:
            resource_image, resource_rect = resource.refresh_display()
            resource_rect.move_ip(start, 0)
            self.image.blit(resource_image, resource_rect)
            # pygame.draw.rect(self.image, "red", resource_rect, 1)
            start += resource_rect.width
        self.rect = self.image.get_rect()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def confirm_proposed_reduction(self):
        for resource in self.resources:
            resource.confirm_proposed_reduction()
        self.compile_ui()
        

