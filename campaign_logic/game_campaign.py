import pygame.mouse

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
import math

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
buildings = pygame.sprite.Group()

mouse_manager = CampaignMouseManager(player)

TILE_SIZE = CAMPAIGN_TILE_SIZE*SCALE
def get_hover_tile_topleft():
    mouse_pos = pygame.mouse.get_pos()
    abs_pos = (pygame.Vector2(mouse_pos) + camera.offset)/TILE_SIZE
    return (
        math.floor(abs_pos[0])*TILE_SIZE-camera.offset[0],
        math.floor(abs_pos[1])*TILE_SIZE-camera.offset[1],
    )


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
                    mouse_manager.click(ui.buttons[0].building)
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
            print("Well hello there!")
            new_building.rect.topleft = pygame.Vector2(get_hover_tile_topleft())+camera.offset
            # if new_building.rect.collide():
            buildings.add(new_building)
            camera.add(new_building)

    pygame.display.update()
    clock.tick(120)
