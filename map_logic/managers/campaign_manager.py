from battle_logic.character_settings.minion_stats import Minion, MINION_TO_STATS
from economy.economy_manager import EconomyManager
from economy.goods import GOOD_STATS
from economy.production_methods.military_production_method import MilitaryProductionMethod
from economy.worker import get_worker_manager, Worker
from map_logic.building_ui import BuildingUI
from map_logic.campaign_map_config import forest_campaign_config, home_node, CampaignMapConfig
from map_logic.managers.mouse_manager import MouseManager
from map_logic.player import PlayerStatus, Player
from ui.resource_topbar import ResourceTopBar, ResourceTracker, WorkerTracker
from settings import *
from utils import get_asset_path

from typing import Dict
from collections import Counter

import threading


import time

player = Player(home_node, forest_campaign_config)

class CampaignManager:
    def __init__(self, screen, campaign_config: CampaignMapConfig, economy_manager: EconomyManager):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.nodes = pygame.sprite.Group()
        self.campaign_config = campaign_config
        self.economy_manager = economy_manager

        self.building_ui = BuildingUI("Buildings", (50,50))
        for building in economy_manager.buildings:
            self.building_ui.add_building(building)
        self.building_ui.compile()

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

        self.threads: List[threading.Thread] = []

    @property
    def all_soldiers(self) -> Dict[Worker, Counter[Minion]]:
        d_soldiers: Dict[Worker, Counter[Minion]] = {}
        for building in self.economy_manager.buildings:
            pm = building.production_method
            if type(pm)==MilitaryProductionMethod:
                print(pm.input_worker)
                print(pm.output_soldier)
                if pm.active_soldiers>0:
                    if pm.input_worker not in d_soldiers:
                        d_soldiers[pm.input_worker] = Counter()
                    d_soldiers[pm.input_worker][pm.output_soldier] = pm.active_soldiers
        return d_soldiers



    def refresh_resources(self):
        """
        Refresh the resource topbar
        :return:
        """
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
                WorkerTracker(
                    worker.value.title(),
                    worker_stats.image_loc,
                    self.economy_manager.unemployed_workers[worker],
                    self.economy_manager.worker_counts[worker],
                )
            )

        all_soldiers = self.all_soldiers.copy()
        for worker in all_soldiers:
            for soldier in all_soldiers[worker]:
                if all_soldiers[worker][soldier]>0:
                    resources.append(
                        ResourceTracker(
                            soldier.name.title(),
                            MINION_TO_STATS[soldier].image_loc,
                            all_soldiers[worker][soldier],
                        )
                    )

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


    def update_economy(self):
        self.economy_manager.tick_economy()
        self.refresh_resources()
        self.building_ui.compile()


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
                    for button in self.building_ui.add_soldier_buttons:
                        if button.is_hovered and self.building_ui.should_display:
                            button.press_button()
                            self.economy_manager.unassign_worker(button.pm.input_worker)
                            self.refresh_resources()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.building_ui.toggle_on()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:
                    self.building_ui.toggle_off()




        self.screen.blit(self.background, (0, 0))
        self.mouse_manager.update()

        self.highlight_hover()
        self.draw_edges()
        self.nodes.draw(self.screen)
        player.update()
        player.draw(self.screen)
        self.resource_topbar.draw(self.screen)

        if self.building_ui.should_display:
            self.building_ui.draw(self.screen)
            # print(len(self.building_ui.sprites))

        # Tick the economy every 10 seconds
        if time.time()-self.checkpoint>1:
            # self.update_economy()
            thread = threading.Thread(target=self.update_economy)
            thread.start()
            # thread.join()
            self.checkpoint += 1
            # self.economy_manager.tick_economy()
            # self.refresh_resources()
            # self.building_ui.refresh()


