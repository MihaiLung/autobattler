from economy.economy_manager import EconomyManager
from economy.goods import GOOD_STATS
from economy.worker import get_worker_manager
from map_logic.campaign_config import forest_campaign_config, home_node, CampaignConfig
from map_logic.managers.mouse_manager import MouseManager
from map_logic.player import PlayerStatus, Player
from ui.resource_topbar import ResourceTopBar, ResourceTracker
from settings import *
from utils import get_asset_path
import time

player = Player(home_node, forest_campaign_config)

class CampaignManager:
    def __init__(self, screen, campaign_config: CampaignConfig, economy_manager: EconomyManager):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.nodes = pygame.sprite.Group()
        self.campaign_config = campaign_config
        self.economy_manager = economy_manager

        for node in campaign_config.d_neighbors:
            self.nodes.add(node)
            for end_node in campaign_config.d_neighbors[node]:
                self.nodes.add(end_node)
        self.triggered_encounter = None

        background = pygame.image.load(get_asset_path("fantasia_mappia.png"))
        self.background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
        self.mouse_manager = MouseManager()
        self.player_path = None


        self.resource_topbar = ResourceTopBar([])
        self.refresh_resources()
        self.checkpoint = time.time()

    def refresh_resources(self):
        # resources = [
        #     ResourceTracker("Wood", "wood_icon.png", 100)
        # ]
        print(self.economy_manager.market.good_markets)
        market_balance = self.economy_manager.market.balance
        resources = []
        for good in market_balance:
            good_stats = GOOD_STATS[good]
            resources.append(
                ResourceTracker(good.value.title(), good_stats.image_loc, market_balance[good])
            )
        for worker in self.economy_manager.worker_counts:
            worker_stats = get_worker_manager(worker)
            resources.append(
                ResourceTracker(
                    worker.value.title(),
                    worker_stats.image_loc,
                    self.economy_manager.worker_counts[worker],
                    self.economy_manager.unemployed_workers[worker]
                )
            )
        print(resources)
        self.resource_topbar.resources = resources
        self.resource_topbar.compile_ui()

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

        # Tick the economy every 10 seconds
        if time.time()-self.checkpoint>1:
            self.checkpoint += 1
            self.economy_manager.tick_economy()
            self.refresh_resources()


