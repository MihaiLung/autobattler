from campaign_logic.buildings import Building
from campaign_logic.campaign_managers.campaign_mouse_manager import CampaignMouseManager
from campaign_logic.campaign_utils import get_hover_tile_topleft
from settings import *
# from campaign_logic.campaign_ui import BuildingUI
from ui.sprite_summon_menu import SpriteSummonUI

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

# ui = BuildingUI()
ui = SpriteSummonUI()
# ui.level = -10
ui.create_button_for_sprite_generation(Building())
ui.compile_ui_buttons()
buildings = pygame.sprite.Group()

mouse_manager = CampaignMouseManager(player)

while True:
    pygame_events = pygame.event.get()
    for event in pygame_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                new_fireball = Fireball(player.position.copy(), pygame.Vector2(pygame.mouse.get_pos())+camera.offset)
                camera.add(new_fireball)
            if event.key == pygame.K_r:
                if mouse_manager.selected_building is not None:
                    mouse_manager.selected_building.rotate_90_degrees()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if ui.rect.collidepoint(pygame.mouse.get_pos()):
                    mouse_manager.click(ui.buttons[0].proto_sprite)
                else:
                    mouse_manager.click()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_manager.unclick()

    screen.fill(pygame.Color("black"))
    camera.update()
    camera.centered_draw(screen)
    ui.draw(screen)
    if mouse_manager.selected_building:
        new_building = mouse_manager.hover(screen, get_hover_tile_topleft(), camera.offset, buildings)
        if new_building is not None:
            new_building.rect.topleft = pygame.Vector2(get_hover_tile_topleft()) + camera.offset
            if pygame.sprite.spritecollideany(new_building, buildings):
                print("NO ME GUSTA >:(")
                new_building.kill()
            else:
                buildings.add(new_building)
                camera.add(new_building)
                print(len(buildings))

    # pygame.draw.rect(screen, pygame.Color("white"), pygame.Rect(*background_chunks.get_chunk_coords_containing_player(), CHUNK_SIZE, CHUNK_SIZE), 10)
    pygame.display.update()
    clock.tick(120)
