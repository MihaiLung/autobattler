import sys
from _ast import Div

import pygame

from economy.production_methods.military_production_method import MilitaryProductionMethod
from settings import WIDTH, HEIGHT

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Building UI")

from economy.production_methods.economic_production_method import ProductionMethod
from economy.buildings import Building
# from economy.goods import Good, GOOD_STATS
# from economy.economy_manager import standard_farming, elven_military
# from economy.worker import Worker, Job, WORKER_MANAGERS
# from utils import load_image, bound_rect_within_screen
# from typing import Optional, Dict
#
#
#
# class UIElement(pygame.sprite.Sprite):
#     def __init__(self, image):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = image
#         self.rect = self.image.get_rect()
#
# class Div:
#     def __init__(
#             self,
#             horizontal: bool=True,
#             margin_between_elements: int = 10,
#             background_color = None,
#             min_width: Optional[int] = None,
#             center = False
#         ):
#         self.ordered_elements = []
#         self.horizontal = horizontal
#         self.margin_between_elements = margin_between_elements
#         self.background_color = background_color
#         self.min_width = min_width
#         self.center = center
#         self.buttons = []
#         self.parent_div: Optional[Div] = None
#
#     def set_parent_div(self, parent_div: Div):
#         self.parent_div = parent_div
#
#     def add_button(self, button: AddSoldierButton):
#         self.ordered_elements.append(UIElement(button.image))
#         self.buttons.append(button)
#         button.rect = self.ordered_elements[-1].rect
#
#     def add_surface(self, element: pygame.Surface):
#         self.ordered_elements.append(UIElement(element))
#
#     def add_div(self, element: 'Div'):
#         self.ordered_elements.append(element.compile_div())
#         element.set_parent_div(self)
#
#     def compile_div(self) -> UIElement:
#         size_tracker = lambda rect: 0
#         if self.horizontal:
#             margin_computation = lambda previous_rect: (previous_rect.right + self.margin_between_elements, 0)
#             if self.center:
#                 size_tracker = lambda rect: rect.height
#         else:
#             margin_computation = lambda previous_rect: (0, previous_rect.bottom+self.margin_between_elements)
#             if self.center:
#                 size_tracker = lambda rect: rect.width
#
#
#
#         overall_rect = self.ordered_elements[0].rect.copy()
#         size = size_tracker(self.ordered_elements[0].rect)
#         for previous_element, element in zip(self.ordered_elements[:-1], self.ordered_elements[1:]):
#             element.rect.move_ip(margin_computation(previous_element.rect))
#             overall_rect.union_ip(element.rect)
#             size = max(size, size_tracker(element.rect))
#
#         if self.center:
#             for element in self.ordered_elements:
#                 if self.horizontal:
#                     element.rect.centery = int(size/2)
#                 else:
#                     element.rect.centerx = int(size/2)
#
#         if self.min_width and self.min_width>0:
#             overall_rect.width = max(self.min_width, overall_rect.width)
#         image = pygame.Surface(overall_rect.size, pygame.SRCALPHA)
#         if self.background_color:
#             image.fill(self.background_color)
#         for element in self.ordered_elements:
#             image.blit(element.image, element.rect)
#         return UIElement(image)
#
#
#
# class BuildingEntry(pygame.sprite.Sprite):
#     FONT = pygame.font.SysFont('timesnewroman', 18)
#     TITLE_FONT = pygame.font.SysFont('timesnewroman', 20, bold=True)
#     ARROW_SURFACE = load_image("arrow.png", (50,50))
#
#     def __init__(self, building: Building):
#         pygame.sprite.Sprite.__init__(self)
#         self.building = building
#         self.pm = building.production_method
#         self.building_icon = load_image(building.image_loc)
#         self.building_icon = pygame.transform.smoothscale(self.building_icon, (50,50))
#         self.building_icon_rect = self.building_icon.get_rect()
#         self.title = self.TITLE_FONT.render(building.name.title(), True, 'black').convert_alpha()
#
#         self.add_soldier_button = None
#         if type(self.pm)==MilitaryProductionMethod:
#             self.add_soldier_button = AddSoldierButton(self.building)
#         print(building.name, self.add_soldier_button)
#
#
#         self.image = None
#         self.rect = None
#
#         self.refresh()
#
#     def get_text_sprite(self, txt):
#         print(txt)
#         return self.FONT.render(txt, True, 'black').convert_alpha()
#
#     @property
#     def capacity_descriptor(self):
#         pm = self.building.production_method
#         job_descs_div = Div(False, 10)
#         for job in pm.job_capacity_demand_per_level:
#             job_desc = Div(False, 5)
#
#             job_max_demand = int(pm.job_capacity_demand_per_level[job] * pm.level)
#             job_supply = int(pm.get_total_job_capacity_supply(job))
#             fulfillment = round(job_supply / job_max_demand * 100, 1)
#
#             desc = f"{job.name.title()}: {job_supply} / {job_max_demand} ({fulfillment}%)"
#             job_desc.add_surface(self.get_text_sprite(desc))
#
#             for worker in pm.workforce[job]:
#                 if pm.workforce[job][worker] > 0:
#                     worker_desc_div = Div(True, center=True)
#                     worker_desc_div.add_surface(self.get_text_sprite("--"))
#
#                     worker_image = load_image(WORKER_MANAGERS[worker].image_loc, (20,20))
#                     worker_desc_div.add_surface(worker_image)
#
#                     contribution_percentage = pm.total_capacity_from_worker_for_job(worker, job) / job_supply
#                     workforce_desc = (
#                         # f" -- {worker.name.title()} x {pm.workforce[job][worker]} "
#                         f"x {pm.workforce[job][worker]} "
#                         f"({contribution_percentage * 100:.0f}% of capacity)"
#                     )
#                     worker_desc_div.add_surface(self.get_text_sprite(workforce_desc))
#                     # job_desc.add_surface(self.get_text_sprite(workforce_desc))
#                     job_desc.add_div(worker_desc_div)
#             job_descs_div.add_div(job_desc)
#         print(job_descs_div)
#
#         return job_descs_div
#
#     def _generate_goods_descriptor(self, goods_dict: Dict[Good, float]) -> Div:
#         goods_descs_div = Div(False, 10)
#         for good in goods_dict:
#             if goods_dict[good] > 0:
#                 good_desc_div = Div(True, 5)
#                 good_desc_div.add_surface(load_image(GOOD_STATS[good].image_loc, (30,30)))
#                 good_desc_div.add_surface(self.get_text_sprite(str(int(goods_dict[good]))))
#                 goods_descs_div.add_div(good_desc_div)
#         return goods_descs_div
#
#     @property
#     def good_consumption_descriptor(self) -> Div:
#         return self._generate_goods_descriptor(self.building.production_method.input_goods_demand)
#
#     @property
#     def good_production_descriptor(self) -> Div:
#         return self._generate_goods_descriptor(self.building.production_method.output_goods_supply)
#
#
#     def refresh(self):
#
#         # Get title div
#         title_div = Div(True)
#
#         # Building image
#         title_div.add_surface(self.building_icon)
#
#         # Building desc
#         description_div = Div(False)
#         description_div.add_surface(self.title)
#         description_div.add_surface(self.get_text_sprite(f"Num levels: {self.building.production_method.level}"))
#         title_div.add_div(description_div)
#
#         if self.add_soldier_button:
#             title_div.add_button(self.add_soldier_button)
#
#         # Production Method
#         production_method_div = Div(True, center=True)
#
#         # -- Inputs
#         inputs_div = Div(False)
#         if len(self.capacity_descriptor.ordered_elements)>0:
#             inputs_div.add_div(self.capacity_descriptor)
#         if len(self.good_consumption_descriptor.ordered_elements)>0:
#             inputs_div.add_div(self.good_consumption_descriptor)
#         if len(inputs_div.ordered_elements)>0:
#             production_method_div.add_div(inputs_div)
#
#         # -- Arrow
#         production_method_div.add_surface(BuildingEntry.ARROW_SURFACE)
#
#         # -- Outputs
#         if len(self.good_production_descriptor.ordered_elements)>0:
#             production_method_div.add_div(self.good_production_descriptor)
#
#         # Production method
#         building_div = Div(False, 20, background_color="silver", min_width=int(WIDTH/3))
#         building_div.add_div(title_div)
#         building_div.add_div(production_method_div)
#
#         self.image = building_div.compile_div().image
#         self.rect = self.image.get_rect()
#         if self.add_soldier_button:
#             self.add_soldier_button.rect.midright = self.rect.midright
#             # self.image.blit(self.add_soldier_button.image, self.add_soldier_button.rect)
#
#     def get_surface(self):
#         if not self.image:
#             self.refresh()
#         return self.image
#
#
#     def draw(self, surface: pygame.Surface, y_offset: int = 0):
#         surface.blit(self.image, self.rect.move(0, y_offset))
#         # if self.add_soldier_button:
#         #     surface.blit(self.add_soldier_button.image, self.add_soldier_button.rect.move(0, y_offset))
#         #     print("Bonjour :)")
#
#
#
# class BuildingUI(pygame.sprite.Sprite):
#     PAPYRUS_COLOR = (235, 213, 179)
#     TITLE_FONT = pygame.font.SysFont('timesnewroman', 30)
#
#
#     def __init__(self, title):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface((WIDTH/3, HEIGHT*0.8))
#         self.rect = self.image.get_rect()
#         self.image.fill(self.PAPYRUS_COLOR)
#
#         self.title = self.TITLE_FONT.render(title, True, "black")
#         title_rect = self.title.get_rect()
#         title_rect.midtop = int(self.rect.width/2), 0
#         self.image.blit(self.title, title_rect)
#
#
#         self.building_entries = []
#         self.add_soldier_buttons = []
#         self.should_display = False
#
#     def add_building(self, building: Building):
#         building_entry = BuildingEntry(building)
#         self.building_entries.append(building_entry)
#         if building_entry.add_soldier_button:
#             self.add_soldier_buttons.append(building_entry.add_soldier_button)
#
#
#     def refresh(self):
#         ui_div = Div(False, 30, background_color=self.PAPYRUS_COLOR)
#         ui_div.add_surface(self.title)
#         for building_entry in self.building_entries:
#             building_entry.refresh()
#             ui_div.add_surface(building_entry.image)
#
#         compiled_ui = ui_div.compile_div()
#         self.image = compiled_ui.image
#         self.rect = compiled_ui.rect.move(50, 80)
#
#         if self.add_soldier_buttons:
#             for soldier_button in self.add_soldier_buttons:
#                 button_rect = soldier_button.rect.copy()
#                 found_none = False
#                 while not found_none:
#                     self.add_building(None)
#
#
#     def draw(self, screen):
#         screen.blit(self.image, self.rect)
#
#     def draw_at_mouse_pos(self, screen):
#         self.rect.midtop = pygame.mouse.get_pos()
#         self.rect = bound_rect_within_screen(self.rect, screen)
#         self.draw(screen)
#
#     def toggle_on(self):
#         self.should_display = True
#
#     def toggle_off(self):
#         self.should_display = False
#
#
# if __name__ == "__main__":
#     clock = pygame.time.Clock()
#     building_ui = BuildingUI("Buildings Registry")
#     building_ui.add_building(Building("Building", "orc_settlement.png", elven_military))
#     building_ui.refresh()
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#                 pygame.quit()
#                 sys.exit()
#         building_ui.draw(screen)
#         pygame.display.update()

