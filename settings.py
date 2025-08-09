import enum
import pygame
from typing import List, Tuple
from battle_logic.character_settings.minion_base_class import MinionStats

pygame.init()

# Screen Settings
WIDTH, HEIGHT = 1600, 900
UI_BUTTON_SIZE = 100
SCALE = 0.5
FONT = pygame.font.SysFont(None, int(24*SCALE))

# Battle Settings
COLLISION_QUADRANT_SIZE = 200
class GameEvents(enum.Enum):
    BattlePlanningDone = pygame.USEREVENT+1
    BattleDone = pygame.USEREVENT+2
    EnterBattlePlanning = pygame.USEREVENT + 3
    EnterCampaignMode = pygame.USEREVENT + 4

# Campaign Settings
CHUNK_SIZE = 1000
CAMPAIGN_TILE_SIZE = 50
CAMPAIGN_GRASS_SIZE = 50
class CampaignDisplayZ(enum.Enum):
    background = 0
    grass = 1
    buildings = 2
    player = 3
    spells = 4

ENEMIES_CONFIG_DTYPE = List[Tuple[MinionStats, int]]
