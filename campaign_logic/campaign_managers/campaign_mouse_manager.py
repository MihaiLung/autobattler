import pygame
import enum
from typing import Optional, Tuple, List
from battle_logic.battle.character import Character, CharacterGroup
from campaign_logic.buildings import Building


class CampaignMouseStates(enum.Enum):
    EMPTY="empty"
    PLANNING_BUILDING="holding"
    SPAWNING="spawning"


class CampaignMouseManager:
    BRIGHT_GREEN = (0, 255, 0)
    SOFT_TRANSPARENT_GREEN = (144, 238, 144, 90)


    def __init__(self):
        self.state = CampaignMouseStates.EMPTY
        self.building: Optional[Building] = None
        self.spawn_timer = 0
        self.click_pos = Tuple[int,int]
        self.character_positions: List[Tuple[int,int]] = []

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

    def unclick(self):
        self.spawn_timer = 0
        if self.state == MouseStates.SPAWNING:
            for pos in self.character_positions:
                self.spawn_character_at_pos(pos)
            self.character_positions = []
            self.state = MouseStates.EMPTY

    def hover(self, screen: pygame.Surface):
        # Always display the character under the mouse, if it's selected
        if self.character is not None:
            self.character.draw(screen, pygame.mouse.get_pos())

        # If the mouse is in spawning mode, draw formations (eg - behaviour after clicking and before releasing)
        if self.state == MouseStates.SPAWNING:
            selection_rect = self.get_selection_rect(pygame.mouse.get_pos())

            self.character_positions = []
            char_side_length = self.character.radius
            for i in range(int(selection_rect.width//char_side_length)):
                for j in range(int(selection_rect.height//char_side_length)):
                    x = i*char_side_length+selection_rect.x
                    y = j*char_side_length+selection_rect.y
                    self.character_positions.append((x, y))
                    screen.blit(self.character.image, (x, y))


            transparent_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
            transparent_surface.fill(MouseManager.SOFT_TRANSPARENT_GREEN)
            screen.blit(transparent_surface, (selection_rect.x, selection_rect.y))


            pygame.draw.rect(
                screen,
                rect=selection_rect,
                color=MouseManager.BRIGHT_GREEN,
                width=8
            )


            # if self.spawn_timer == 0:
            #     new_char = self.character.copy()
            #     new_char.set_position_center(pygame.mouse.get_pos())
            #     self.team.add(new_char)
            #     self.spawn_timer = MouseManager.SPAWN_COOLDOWN
            # self.spawn_timer -= 1