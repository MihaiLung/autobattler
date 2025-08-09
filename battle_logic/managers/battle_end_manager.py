import pygame

from battle_logic.managers.battle_manager import BattleManager
from map_logic.encounter_icon import CircularImageSprite
from settings import *
from ui.buttons import Button


button_restart_game = Button(
    text='Restart Game',
    rect=pygame.Rect(int(WIDTH/2)-100,int(HEIGHT/2)-100, 200, 80),
    # button_press_event=pygame.event.Event(GameEvents.EnterBattlePlanning.value),
    button_press_event=pygame.event.Event(GameEvents.EnterCampaignMode.value),
)

class BattleOutcomeManager:
    def __init__(self, battle_manager: BattleManager, screen, encounter: CircularImageSprite):
        win = len(battle_manager.allied_group)>0
        if win:
            text = "You win! Congratulations!"
            encounter.is_cleared = True
            encounter.refresh_image()
        else:
            text = "You lost :( Better luck next time bestie!"
        self.battle_manager = battle_manager
        self.text = text
        self.font = pygame.font.Font(None, 40)

        self.text_surface = self.font.render(text, True, (0,0,0))
        self.text_rect = self.text_surface.get_rect(center=(int(WIDTH/2),int(HEIGHT/2)))
        self.screen = screen

    def update(self, pygame_events):
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_restart_game.rect.collidepoint(pygame.mouse.get_pos()):
                    button_restart_game.button_press()

        self.battle_manager.draw()
        self.screen.blit(self.text_surface, self.text_rect)
        button_restart_game.draw(self.screen)