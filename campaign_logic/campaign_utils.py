import math

import pygame.mouse

from campaign_logic.game_campaign import camera
from settings import CAMPAIGN_TILE_SIZE


def get_hover_tile_topleft():
    mouse_pos = pygame.mouse.get_pos()
    abs_pos = (pygame.Vector2(mouse_pos) + camera.offset)/CAMPAIGN_TILE_SIZE
    return (
        math.floor(abs_pos[0])*CAMPAIGN_TILE_SIZE-camera.offset[0],
        math.floor(abs_pos[1])*CAMPAIGN_TILE_SIZE-camera.offset[1],
    )

def shift_tile_coordinates(tile_coordinates, left: int = 0, down: int = 0) -> tuple[int, int]:
    return (tile_coordinates[0] + left*CAMPAIGN_TILE_SIZE, tile_coordinates[1] + down*CAMPAIGN_TILE_SIZE)