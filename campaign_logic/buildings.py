import pygame
import pygame.image
import pygame.sprite
import pygame.transform
from settings import *

# class ConveyorRotations(enum.Enum):
#     LEFT = lambda x: x
#     RIGHT = lambda x: pygame.transform.rotate(x, 180)
#     UP = lambda x: pygame.transform.rotate(x, 90)
#     DOWN = lambda x: pygame.transform.rotate(x, 270)
#
# def get_next_rotation(current_rotation: ConveyorRotations) -> ConveyorRotations:
#     """
#     Returns the next 90-degree clockwise rotation for a given ConveyorRotations enum member.
#     """
#     rotation_order = [
#         ConveyorRotations.LEFT,
#         ConveyorRotations.UP,
#         ConveyorRotations.RIGHT,
#         ConveyorRotations.DOWN
#     ]
#     current_index = rotation_order.index(current_rotation)
#     next_index = (current_index + 1) % len(rotation_order)
#     return rotation_order[next_index]

class ConveyorAngle(enum.Enum):
    LEFT = 0
    UP = 90
    RIGHT = 180
    DOWN = 270

class Building(pygame.sprite.Sprite):
    def __init__(self, size=None, angle=ConveyorAngle.LEFT.value):
        pygame.sprite.Sprite.__init__(self)
        if not size:
            self.size = CAMPAIGN_TILE_SIZE
        else:
            self.size = size
        self.angle = angle
        self.load_image()
        # self.image = self.direction(self.image, angle)
        self.can_rotate = True
        self.level=CampaignDisplayZ.buildings.value
        self.image_path = "../assets/magical_conveyor.png"

    def load_image(self):
        self.image = pygame.image.load("../assets/magical_conveyor.png")
        if self.angle!=0:
            self.image = pygame.transform.rotate(self.image, self.angle)
        self.size = self.size
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect()

    def rotate_90_degrees(self):
        self.angle = (self.angle - 90) % 360
        self.load_image()



    @property
    def image_raw(self):
        return self.image.copy()

    def copy(self):
        new_conveyor = Building(None, angle=self.angle)
        new_conveyor.image = self.image.copy()
        new_conveyor.rect = self.rect.copy()
        return new_conveyor

    def draw(self, screen, topleft):
        draw_rect = self.rect.copy()
        draw_rect.topleft = topleft
        screen.blit(self.image, draw_rect)