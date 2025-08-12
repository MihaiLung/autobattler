import enum

import networkx as nx
import numpy as np
import pygame

from map_logic.campaign_config import forest_campaign_config, CampaignConfig
from tuple_utils import tdiff
from utils import get_asset_path


class PlayerStatus(enum.Enum):
    AT_NODE=1,
    MOVING=2


class Player(pygame.sprite.Sprite):
    def __init__(self, home_node, campaign_config: CampaignConfig):
        self.image = pygame.image.load(get_asset_path("pc.png")).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (100,100))
        self.is_facing_left = False
        self.rect = self.image.get_rect()

        self.campaign_config = campaign_config

        self.direction = None
        self.traveled_so_far = None
        self.distance_to_travel = None

        self.travel_path = []

        self.hover_point = 0

        self.locate_at_node(home_node)

    def compute_path_to_node(self, node):
        return self.campaign_config.get_shortest_path(self.current_node, node)

    def flip(self):
        self.is_facing_left = not self.is_facing_left
        self.image = pygame.transform.flip(self.image, True, False)

    def locate_at_node(self, node):
        self.status = PlayerStatus.AT_NODE
        self.current_node = node
        self.target_node = None
        self.rect.midbottom = node.rect.midtop
        # self.actual_rect = self.rect.copy()
        self.position = pygame.Vector2(self.rect.center)

    def draw(self, screen):
        if self.status == PlayerStatus.AT_NODE:
            screen.blit(self.image, self.rect.move(0, np.sin(np.radians(self.hover_point))*4))
            self.hover_point += 3
        else:
            screen.blit(self.image, self.rect)

    def start_move_to_node(self, node):
        # self.rect = self.actual_rect.copy()
        self.target_node = node
        self.status = PlayerStatus.MOVING
        self.traveled_so_far = 0
        offset = pygame.Vector2(tdiff(self.target_node.rect.center, self.current_node.rect.center))
        self.direction = offset.normalize()*5
        self.distance_to_travel = offset.magnitude()

        if self.is_facing_left and self.direction[0]>0:
            self.flip()
        elif (not self.is_facing_left) and self.direction[0]<0:
            self.flip()

    def update_rect_position(self):
        self.rect.center = int(self.position[0]), int(self.position[1])

    def update(self):
        # If moving, increment the player's position towards the destination
        if self.status == PlayerStatus.MOVING:
            self.position += self.direction
            self.update_rect_position()
            self.traveled_so_far += self.direction.magnitude()
            if self.traveled_so_far >= self.distance_to_travel:
                self.locate_at_node(self.target_node)
                if len(self.travel_path)>0:
                    self.travel_path.pop(0)
        elif self.status == PlayerStatus.AT_NODE:
            if len(self.travel_path)>0:
                self.start_move_to_node(self.travel_path[0])
