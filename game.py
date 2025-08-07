from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from sys import exit
from battle_logic.managers.battle_manager import BattleManager
from ui.buttons import Button
from battle_logic.character import Character, CharacterGroup
from battle_logic.character_settings.minion_stats import elf_stats, orc_stats
from battle_logic.managers.battle_planning_manager import BattlePlanningManager
from battle_logic.managers.battle_end_manager import BattleOutcomeManager

from battle_logic.logic.utils import *


class GameState(enum.Enum):
    BATTLE_PREP='battle_prep',
    BATTLE='battle',
    BATTLE_OUTCOME_SCREEN='battle_outcome_screen',

pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()


camera = pygame.sprite.Group()

orc_group = CharacterGroup()
elf_group = CharacterGroup()
all_group = CharacterGroup()

attack_animations = pygame.sprite.Group()

proto_orc = Character(orc_stats)
proto_elf = Character(elf_stats)


battle_planning_manager = BattlePlanningManager([proto_elf], [proto_orc], screen)
game_state = GameState.BATTLE_PREP

while True:
    pygame_events = pygame.event.get()
    for event in pygame_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == GameEvents.BattlePlanningDone.value:
            # If player signalled planning is done, transfer setup to battle manager and run battle
            battle_manager = BattleManager(
                battle_planning_manager.allied_group,
                battle_planning_manager.enemy_group,
                screen
            )
            game_state = GameState.BATTLE
        if event.type == GameEvents.BattleDone.value:
            battle_outcome_manager = BattleOutcomeManager(battle_manager, screen)
            game_state = GameState.BATTLE_OUTCOME_SCREEN
        if event.type == GameEvents.RestartGame.value:
            battle_planning_manager = BattlePlanningManager([proto_elf], [proto_orc], screen)
            game_state = GameState.BATTLE_PREP


    if game_state == GameState.BATTLE_PREP:
        battle_planning_manager.update(pygame_events)
    elif game_state == GameState.BATTLE:
        battle_manager.update()
    elif game_state == GameState.BATTLE_OUTCOME_SCREEN:
        battle_outcome_manager.update(pygame_events)




    pygame.display.update()
    clock.tick(120)
