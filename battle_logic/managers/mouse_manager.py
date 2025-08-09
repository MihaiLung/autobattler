import pygame
import enum
from typing import Optional, Tuple, List
from battle_logic.character import Character, CharacterGroup
from settings import HEIGHT


class MouseStates(enum.Enum):
    EMPTY="empty"
    HOLDS_CHARACTER="holding"
    SPAWNING="spawning"



class MouseManager:
    SPAWN_COOLDOWN = 20
    BRIGHT_GREEN = (0, 255, 0)
    SOFT_TRANSPARENT_GREEN = (144, 238, 144, 90)


    def __init__(self):
        self.state = MouseStates.EMPTY
        self.character: Optional[Character] = None
        self.team: Optional[CharacterGroup] = None
        self.spawn_timer = 0
        self.click_pos = Tuple[int,int]
        self.character_positions: List[Tuple[int,int]] = []

    def get_selection_rect(self, pos) -> pygame.Rect:
        x = int(min(self.click_pos[0], pos[0]))
        y = int(min(self.click_pos[1], pos[1]))
        width = abs(self.click_pos[0]-pos[0])
        height = abs(self.click_pos[1]-pos[1])
        # print(pygame.Rect(x, y, width, height))
        return pygame.Rect(x, y, width, height)

    @staticmethod
    def cap_mouse_location(pos: Tuple[int, int])-> Tuple[int, int]:
        return pos[0], int(max(HEIGHT/2, pos[1]))

    def click(self, character: Optional[Character] = None, team: Optional[CharacterGroup] = None):
        # If pressed outside UI:
        if character is None:
            if self.character is not None:
                self.state = MouseStates.SPAWNING

        # If pressed in UI
        else:
            self.state = MouseStates.HOLDS_CHARACTER
            self.character = character.copy()
            self.team = team

        self.click_pos = self.cap_mouse_location(pygame.mouse.get_pos())

    def spawn_character_at_pos(self, pos: Tuple[int,int]):
        new_char = self.character.copy()
        new_char.set_position_topleft(pos)
        self.team.add(new_char)

    def unclick(self):
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
            selection_rect = self.get_selection_rect(self.cap_mouse_location(pygame.mouse.get_pos()))

            self.character_positions = []
            char_side_length = self.character.diameter
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
