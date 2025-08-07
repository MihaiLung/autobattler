from typing import Optional, Tuple, List
from campaign_logic.buildings import Building
from campaign_logic.player import Player
from settings import *

# from campaign_logic.buildings import ConveyorRotations

# class RKeyRotations(enum.Enum):
#     ConveyorRotations.LEFT = ConveyorRotations.DOWN
#     ConveyorRotations.DOWN = ConveyorRotations.RIGHT
#     ConveyorRotations.RIGHT = ConveyorRotations.UP
#     ConveyorRotations.UP = ConveyorRotations.LEFT

class CampaignMouseStates(enum.Enum):
    EMPTY="empty"
    HOLDING="holding"
    SPAWNING="spawning"

class CampaignMouseManager:
    BRIGHT_GREEN = (0, 255, 0)
    SOFT_TRANSPARENT_GREEN = (144, 238, 144, 90)


    def __init__(self, player: Player):
        self.state = CampaignMouseStates.EMPTY
        self.selected_building: Optional[Building] = None
        self.spawn_timer = 0
        self.click_pos = Tuple[int,int]
        self.character_positions: List[Tuple[int,int]] = []
        self.player = player

    @property
    def tile_size(self):
        return int(CAMPAIGN_TILE_SIZE*SCALE)

    def click(self, newly_selected_building: Optional[Building] = None):
        # If pressed outside UI:
        if newly_selected_building is None:
            # If holding a building, start a-building
            if self.selected_building is not None:
                # return self.selected_building.copy()
                self.state = CampaignMouseStates.SPAWNING
            # Otherwise, pass
            else:
                pass
        # If pressed in UI, select new building
        else:
            self.state = CampaignMouseStates.HOLDING
            self.selected_building = newly_selected_building.copy()

        self.click_pos = pygame.mouse.get_pos()

    def spawn_character_at_pos(self, pos: Tuple[int,int]):
        new_char = self.character.copy()
        new_char.set_position_topleft(pos)
        self.team.add(new_char)

    def unclick(self):
        if self.state == CampaignMouseStates.SPAWNING:
            self.state = CampaignMouseStates.HOLDING

    def hover(self, screen: pygame.Surface, hover_tile: tuple[int, int], offset: Tuple[int,int], buildings: pygame.sprite.Group):
        # Always display the sprite under the mouse, if it's selected
        if self.selected_building is not None:
            self.selected_building.draw(screen, hover_tile)

        # If a sprite is selected and in spawning mode,
        if self.state == CampaignMouseStates.SPAWNING:
            map_pos = pygame.Vector2(hover_tile)+offset
            free = True
            for sprite in buildings:
                if sprite.rect.collidepoint(map_pos):
                    free = False
                    print("NO ME GUSTA >:(")
            if free:
                print("HELLO LADIES ;)")
                return self.selected_building.copy()
        return None
