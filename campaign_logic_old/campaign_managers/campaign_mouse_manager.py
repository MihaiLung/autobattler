import pygame
import enum
from typing import Optional, Tuple, List
from battle_logic.battle.character import Character, CharacterGroup
from campaign_logic.buildings import Building
from campaign_logic.player import Player
from settings import *


class CampaignMouseStates(enum.Enum):
    EMPTY="empty"
    PLANNING_BUILDING="holding"
    SPAWNING="spawning"


class CampaignMouseManager:
    BRIGHT_GREEN = (0, 255, 0)
    SOFT_TRANSPARENT_GREEN = (144, 238, 144, 90)


    def __init__(self, player: Player):
        self.state = CampaignMouseStates.EMPTY
        self.building: Optional[Building] = None
        self.spawn_timer = 0
        self.click_pos = Tuple[int,int]
        self.character_positions: List[Tuple[int,int]] = []
        self.player = player

    @property
    def tile_size(self):
        return int(CAMPAIGN_TILE_SIZE*SCALE)

    def click(self, building: Optional[Building] = None, team: Optional[CharacterGroup] = None):
        # If pressed outside UI:
        if building is None:
            if self.building is not None:
                self.state = CampaignMouseStates.PLANNING_BUILDING

        # If pressed in UI
        else:
            self.state = CampaignMouseStates.PLANNING_BUILDING
            self.building = building.copy()
            self.team = team

        self.click_pos = pygame.mouse.get_pos()

    def spawn_character_at_pos(self, pos: Tuple[int,int]):
        new_char = self.character.copy()
        new_char.set_position_topleft(pos)
        self.team.add(new_char)

    # def unclick(self):
    #     self.spawn_timer = 0
    #     if self.state == MouseStates.SPAWNING:
    #         for pos in self.character_positions:
    #             self.spawn_character_at_pos(pos)
    #         self.character_positions = []
    #         self.state = MouseStates.EMPTY

    def hover(self, screen: pygame.Surface):
        # Always display the character under the mouse, if it's selected
        if self.building is not None:
            absolute_pos = pygame.Vector2(pygame.mouse.get_pos())-pygame.Vector2(screen.get_rect().centerx)
            self.building.draw(screen, pygame.mouse.get_pos())