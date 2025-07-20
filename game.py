from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from battle_logic.managers.battle_planning_manager import BattlePlanningManager
from sys import exit
from battle_logic.managers.battle_manager import BattleManager
from user_interface import Button
from battle_logic.battle.character import Character, CharacterGroup
from battle_logic.character_settings.minion_stats import elf_stats, orc_stats

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


button_restart_game = Button(
    text='Restart Game',
    rect=pygame.Rect(int(WIDTH/2)-100,int(HEIGHT/2)-100, 200, 80),
    button_press_event=pygame.event.Event(GameEvents.RestartGame.value),
)

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
            if len(battle_manager.allied_group.sprites())>0:
                player_won = True
            else:
                player_won = False
            if player_won:
                text = "You win! Congratulations!"
            else:
                text = "You lost :( Better luck next time bestie!"
            game_state = GameState.BATTLE_OUTCOME_SCREEN
        if event.type == GameEvents.RestartGame.value:
            battle_planning_manager = BattlePlanningManager([proto_elf], [proto_orc], screen)
            game_state = GameState.BATTLE_PREP
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == GameState.BATTLE_OUTCOME_SCREEN:
            if button_restart_game.rect.collidepoint(pygame.mouse.get_pos()):
                button_restart_game.button_press()

    if game_state == GameState.BATTLE_PREP:
        battle_planning_manager.update(pygame_events)
    elif game_state == GameState.BATTLE:
        battle_manager.update()
    elif game_state == GameState.BATTLE_OUTCOME_SCREEN:
        battle_manager.draw()
        font = pygame.font.Font(None, 40)
        text_surface = font.render(text, True, (0,0,0))
        text_rect = text_surface.get_rect(center=(int(WIDTH/2),int(HEIGHT/2)))
        screen.blit(text_surface, text_rect)
        button_restart_game.draw(screen)




    pygame.display.update()
    clock.tick(120)
