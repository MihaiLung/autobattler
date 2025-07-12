import pygame
import enum
from typing import Optional
from character import Character

class MouseStates(enum.Enum):
    EMPTY="empty"
    HOLDS_CHARACTER="holding"
    SPAWNING="spawning"


class MouseManager:
    SPAWN_COOLDOWN = 20

    def __init__(self):
        self.state = MouseStates.EMPTY
        self.character: Optional[Character] = None
        self.spawn_timer = 0

    def click(self, character: Optional[Character] = None):
        # If pressed outside UI:
        if character is None:
            # If no
            if self.character is not None:
                # Reset
                self.state = MouseStates.SPAWNING
                # self.character = None

        # If pressed in UI
        else:
            self.state = MouseStates.HOLDS_CHARACTER
            self.character = character.copy()


    def unclick(self):
        self.spawn_timer = 0
        if self.state == MouseStates.SPAWNING:
            self.character = None
            self.state = MouseStates.EMPTY
            # if self.character is None:
            #     self.state = MouseStates.EMPTY
            # else:
            #     self.state = MouseStates.HOLDS_CHARACTER

    def hover(self, screen: pygame.Surface, elf_group, orc_group, all_group):
        if self.character is not None:
            self.character.draw(screen, pygame.mouse.get_pos())
        # if self.state == MouseStates.SPAWNING:
        #     if self.spawn_timer == 0:
        #         new_char = self.character.copy()
        #         new_char.position = pygame.Vector2(pygame.mouse.get_pos())
        #         side = elf_group if "elf" in new_char.stats.image_loc else orc_group
        #         side.add(new_char)
        #         all_group.add(new_char)
        #         self.spawn_timer = MouseManager.SPAWN_COOLDOWN
        #     self.spawn_timer -= 1