from map_logic.campaign_config import forest_campaign_config, home_node
from map_logic.managers.mouse_manager import MouseManager
from map_logic.player import PlayerStatus, Player
from ui.resource_manager import ResourceTopBar, ResourceTracker
from settings import *
from utils import get_asset_path

player = Player(home_node, forest_campaign_config)

class CampaignManager:
    def __init__(self, screen, campaign_config):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.nodes = pygame.sprite.Group()
        for node in campaign_config.d_neighbors:
            self.nodes.add(node)
            for end_node in campaign_config.d_neighbors[node]:
                self.nodes.add(end_node)
        # self.nodes.add(wolf_node)
        # self.nodes.add(wolf_node_2)
        self.triggered_encounter = None

        background = pygame.image.load(get_asset_path("fantasia_mappia.png"))
        self.background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
        self.mouse_manager = MouseManager()
        self.player_path = None

        resources = [
            ResourceTracker("Wood", "wood_icon.png", 100)
        ]
        self.resource_topbar = ResourceTopBar(resources)


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
        for (start_node, end_node) in forest_campaign_config.edges:
            pygame.draw.line(self.screen, "red", start_node.rect.center, end_node.rect.center, width=5)


    def update(self, pygame_events):

        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for node in self.nodes:
                        if player.status==PlayerStatus.AT_NODE:
                            if node.rect.collidepoint(pygame.mouse.get_pos()):
                                # If the clicked node is a neighbour node, move there
                                if node in forest_campaign_config.d_neighbors[player.current_node] and (player.status is not PlayerStatus.MOVING):
                                    player.start_move_to_node(node)
                                # If the clicked node is where the player already is, initiate battle
                                elif node==player.current_node and (player.status == PlayerStatus.AT_NODE):
                                    if not node.is_cleared:
                                        event = pygame.event.Event(GameEvents.EnterBattlePlanning.value)
                                        pygame.event.post(event)
                                        self.triggered_encounter = node
                                # Otherwise, compute the best path to target node
                                else:
                                    player.travel_path = player.compute_path_to_node(node)



        self.screen.blit(self.background, (0, 0))
        self.mouse_manager.update()

        self.highlight_hover()
        self.draw_edges()
        self.nodes.draw(self.screen)
        player.update()
        player.draw(self.screen)
        self.resource_topbar.draw(self.screen)


