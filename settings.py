import enum
import pygame


pygame.init()
WIDTH, HEIGHT = 1600, 900

UI_BUTTON_SIZE = 100

COLLISION_QUADRANT_SIZE = 200

SCALE = 0.5

FONT = pygame.font.SysFont(None, int(24*SCALE))

class GameEvents(enum.Enum):
    BattlePlanningDone = pygame.USEREVENT+1
    BattleDone = pygame.USEREVENT+2
    RestartGame = pygame.USEREVENT+3


CHUNK_SIZE = 1000
CAMPAIGN_TILE_SIZE = 50
