# from settings import *
# from settings import WIDTH
#
#
# class BuildingButton(pygame.sprite.Sprite):
#     def __init__(self, building):
#         pygame.sprite.Sprite.__init__(self)
#         self.building = building.copy()
#         self.building_icon = building.copy()
#         self.building_icon.load_image(UI_BUTTON_SIZE*SCALE)
#
#         self.image = self.building_icon.image.copy()
#         self.rect = self.building_icon.rect.copy()
#
#     def build_building(self, position: pygame.Vector2):
#         new_building = self.building.copy()
#         new_building.position = position
#         return new_building
#
#
# class BuildingUI(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#         self.buttons = []
#         self.image = pygame.Surface((0,0))
#         self.rect = self.image.get_rect()
#
#
#     def _create_button_for_building(self, building):
#         self.buttons.append(BuildingButton(building))
#
#     def compile_ui_buttons(self):
#         left_offset = 0
#         width = UI_BUTTON_SIZE*len(self.buttons)
#         self.image = pygame.Surface((width, UI_BUTTON_SIZE))
#         self.image.fill('white')
#         for button in self.buttons:
#             print(button)
#             button.rect.left += left_offset
#             self.image.blit(button.image, button.rect)
#             left_offset += button.rect.width
#         self.rect = self.image.get_rect()
#         self.rect.bottom = HEIGHT
#         self.rect.centerx = WIDTH//2
#
#     def draw(self, screen):
#         screen.blit(self.image, self.rect)
#
