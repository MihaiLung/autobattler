from campaign_logic.buildings import Building
from campaign_logic.campaign_managers.campaign_mouse_manager import CampaignMouseManager
from settings import *
from campaign_logic.campaign_ui import BuildingUI

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT) )

from campaign_logic.background import BackgroundChunks
from campaign_logic.player import Player
from campaign_logic.powah import Fireball
from player_camera import PlayerCamera

pygame.display.set_caption("World of VAVAVAVA")
clock = pygame.time.Clock()
player = Player()
fireballs = pygame.sprite.Group()

camera = PlayerCamera(player)
background_chunks = BackgroundChunks(player)
camera.add(player, fireballs, background_chunks)
camera_center = pygame.Vector2(WIDTH / 2, HEIGHT / 2)

ui = BuildingUI()
ui.level = -10
ui._create_button_for_building(Building())
ui.compile_ui_buttons()
print(ui.image)
print(ui.buttons)

mouse_manager = CampaignMouseManager(player)

while True:
    pygame_events = pygame.event.get()
    for event in pygame_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                new_fireball = Fireball(player.position.copy(), pygame.Vector2(pygame.mouse.get_pos())-camera.offset)
                camera.add(new_fireball)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if ui.rect.collidepoint(pygame.mouse.get_pos()):
                    mouse_manager.click(ui.buttons[0].selected_building)

    screen.fill(pygame.Color("black"))
    camera.update()
    camera.centered_draw(screen)
    ui.draw(screen)
    mouse_manager.hover(screen)

    pygame.display.update()
    clock.tick(120)
