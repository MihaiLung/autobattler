import pygame

from battle_logic.character_settings.minion_stats import orc_stats
from map_logic.mouse_manager import MouseManager
from settings import *
from map_logic.encounter_icon import CircularImageSprite
from utils import get_asset_path



home_node = CircularImageSprite("elf_settlement.png", (0.9, 0.3))
wolf_node = CircularImageSprite("goodboy.png", (0.5, 0.5), [(orc_stats, 5)])
wolf_node_2 = CircularImageSprite("goodboy.png", (0.6, 0.7), [(orc_stats, 15)])
wolf_node_3 = CircularImageSprite("goodboy.png", (0.6, 0.9), [(orc_stats, 29)])

edges = {
    home_node: [wolf_node],
    wolf_node: [wolf_node_2],
    wolf_node_2: [wolf_node_3],
}

class CampaignManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.nodes = pygame.sprite.Group()
        for node in edges:
            self.nodes.add(node)
            for end_node in edges[node]:
                self.nodes.add(end_node)
        # self.nodes.add(wolf_node)
        # self.nodes.add(wolf_node_2)
        self.triggered_encounter = None

        background = pygame.image.load(get_asset_path("fantasia_mappia.png"))
        self.background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
        self.mouse_manager = MouseManager()


    def highlight_hover(self):
        for node in self.nodes:
            if node.rect.collidepoint(pygame.mouse.get_pos()):
                if not node.is_highlighted:
                    node.is_highlighted = True
                    node.refresh_image(True)
            else:
                if node.is_highlighted:
                    node.is_highlighted = False
                    node.refresh_image(False)

    def draw_edges(self):
        """
        Draw edges between location nodes.
        """
        for node in edges:
            for neighbor in edges[node]:
                pygame.draw.line(self.screen, "red", node.rect.center, neighbor.rect.center, width=5)



    def update(self, pygame_events):

        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for node in self.nodes:
                        if not node.is_cleared:
                            if node.rect.collidepoint(pygame.mouse.get_pos()):
                                event = pygame.event.Event(GameEvents.EnterBattlePlanning.value)
                                pygame.event.post(event)
                                self.triggered_encounter = node
        self.screen.blit(self.background, (0, 0))
        self.mouse_manager.update()

        self.highlight_hover()
        self.draw_edges()
        self.nodes.draw(self.screen)
