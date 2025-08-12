import time
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from sys import exit
from map_logic.managers.campaign_manager import CampaignManager

from battle_logic.managers.battle_manager import BattleManager
from battle_logic.character_settings.minion_stats import elf_stats
from battle_logic.managers.battle_planning_manager import BattlePlanningManager
from battle_logic.managers.battle_end_manager import BattleOutcomeManager
from map_logic.campaign_config import forest_campaign_config
from economy.economy_manager import economy_manager

from battle_logic.logic.utils import *

pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()

allies_config = [
    elf_stats,
]



# Start up game
campaign_manager = CampaignManager(screen, forest_campaign_config)
active_manager = campaign_manager
game_state = GameState.CAMPAIGN_MAP
triggered_encounter = None

checkpoint = time.time()
while True:
    pygame_events = pygame.event.get()
    for event in pygame_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == GameEvents.BattlePlanningDone.value:
            print(f"Num elfs: {len(active_manager.allied_group)}")
            print(f"Num orcs: {len(active_manager.enemy_group)}")

            # If player signalled planning is done, transfer setup to battle manager and run battle
            battle_manager = BattleManager(
                active_manager.allied_group,
                active_manager.enemy_group,
                screen
            )
            active_manager = battle_manager
            game_state = GameState.BATTLE
        if event.type == GameEvents.BattleDone.value:
            battle_outcome_manager = BattleOutcomeManager(battle_manager, screen, triggered_encounter)
            active_manager = battle_outcome_manager
            game_state = GameState.BATTLE_OUTCOME_SCREEN
        if event.type == GameEvents.EnterBattlePlanning.value:
            # Assumed only way to trigger an encounter is via the campaign manager
            triggered_encounter = campaign_manager.triggered_encounter
            enemies_config = triggered_encounter.enemies_config
            if enemies_config:
                battle_planning_manager = BattlePlanningManager(allies_config, enemies_config, screen)
                active_manager = battle_planning_manager
                game_state = GameState.BATTLE_PREP
        if event.type == GameEvents.EnterCampaignMode.value:
            campaign_manager = CampaignManager(screen, campaign_config=forest_campaign_config, economy_manager=economy_manager)
            active_manager = campaign_manager

    active_manager.update(pygame_events)
    if type(active_manager)==CampaignManager:
        # Tick the economy every 10 seconds
        if time.time()-checkpoint>10*60:
            checkpoint += 10*60
            economy_manager.tick_economy()



    pygame.display.update()
    clock.tick(120)
