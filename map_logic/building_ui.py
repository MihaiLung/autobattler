import sys
from _ast import Div

import pygame

from battle_logic.character_settings.minion_stats import MINION_TO_STATS
from economy.production_methods.military_production_method import MilitaryProductionMethod
from settings import WIDTH, HEIGHT

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Building UI")

from economy.buildings import Building
from economy.goods import Good, GOOD_STATS
from economy.economy_manager import standard_farming, elven_military, standard_woodcutting
from economy.worker import Worker, Job, WORKER_MANAGERS
from utils import load_image, bound_rect_within_screen, tadd
from typing import Optional, Dict, List, Tuple



class Div:

    def __init__(
            self,
            horizontal: bool=True,
            margin_between_elements: int = 10,
            background_color = None,
            min_width: Optional[int] = None,
            center = False
    ):
        self.horizontal = horizontal
        self.margin_between_elements = margin_between_elements
        self.background_color = background_color
        self.min_width = min_width
        self.center = center

        self.rect = None

        self.ordered_elements = []

        self._parent = None

    @property
    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def add_sprites(self, sprite: pygame.sprite.Sprite):
        self.ordered_elements.append(sprite)


    def add_div(self, div: 'Div'):
        self.ordered_elements.append(div)
        div.set_parent(self)

    def get_all_descendants_with_offset(self, offset: Tuple[int, int]) -> List[pygame.sprite.Sprite]:
        """
        Iteratively goes through all elements in this div and collects all sprites regardless of depth.
        """
        if self.rect is None:
            self.compile()
        sprites = []
        for element in self.ordered_elements:
            if type(element) is Div:
                sprites.extend(element.get_all_descendants_with_offset(tadd(element.rect.topleft, offset)))
            else:
                element.rect.move_ip(offset)
                sprites.append(element)
        return sprites


    def compile(self):
        """
        This function:
         - computes the rect size
         - aligns all the divs of child sprites correctly
         - aligns the child divs appropriately
        """
        # Set up centering and alignment logic
        if len(self.ordered_elements)>0:
            size_tracker = lambda rect: 0
            if self.horizontal:
                margin_computation = lambda previous_rect: (previous_rect.right + self.margin_between_elements, 0)
                if self.center:
                    size_tracker = lambda rect: rect.height
            else:
                margin_computation = lambda previous_rect: (0, previous_rect.bottom+self.margin_between_elements)
                if self.center:
                    size_tracker = lambda rect: rect.width

            # Reset all elements
            for element in self.ordered_elements:
                if type(element)==Div:
                    element.compile() # This should have a rect containing its elements that can be interacted with
                else:
                    element.rect = element.image.get_rect()

            # Align elements
            self.rect = self.ordered_elements[0].rect.copy()
            size = size_tracker(self.ordered_elements[0].rect)
            for previous_element, element in zip(self.ordered_elements[:-1], self.ordered_elements[1:]):
                element.rect.move_ip(margin_computation(previous_element.rect))
                self.rect.union_ip(element.rect)
                size = max(size, size_tracker(element.rect))
            # Center elements
            if self.center:
                for element in self.ordered_elements:
                    if self.horizontal:
                        element.rect.centery = int(size/2)
                    else:
                        element.rect.centerx = int(size/2)

            # Apply min width
            if self.min_width and self.min_width>0:
                self.rect.width = max(self.min_width, self.rect.width)
            if self.background_color:
                background = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
                background.fill(self.background_color)
                self.ordered_elements = [UIElement(background)]+self.ordered_elements

            for sprite in self.ordered_elements:
                if type(sprite) is AddSoldierButton:
                    for sprite in self.ordered_elements:
                        print(type(sprite))
                        print(sprite.rect)
                    print("-"*100)
                    # print(self.rect)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)


class AddSoldierButton(pygame.sprite.Sprite):
    IMAGE_LOC = "add_user_button.png"
    def __init__(self, building: Building):
        pygame.sprite.Sprite.__init__(self)
        self.building = building
        self.pm = building.production_method
        if type(building.production_method) != MilitaryProductionMethod:
            raise ValueError("Trying to add soldier button for non-military production method!")
        self.button_press_effect = self.pm.add_soldiers

        self.image = load_image(self.IMAGE_LOC, (50, 50))
        self.rect = self.image.get_rect()

    @property
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def press_button(self):
        self.button_press_effect(1)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)


class UIElement(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()


class BuildingEntry:
    FONT = pygame.font.SysFont('timesnewroman', 18)
    TITLE_FONT = pygame.font.SysFont('timesnewroman', 20, bold=True)
    ARROW_SURFACE = load_image("arrow.png", (50,50))
    UNIT_ICON_SIZE = (30,30)

    def __init__(self, building: Building):
        self.building = building
        self.pm = building.production_method
        self.building_icon = load_image(building.image_loc)
        self.building_icon = pygame.transform.smoothscale(self.building_icon, (50,50))
        self.building_icon_rect = self.building_icon.get_rect()
        self.title = self.TITLE_FONT.render(building.name.title(), True, 'black').convert_alpha()

        self.add_soldier_button = None
        if type(self.pm)==MilitaryProductionMethod:
            self.add_soldier_button = AddSoldierButton(self.building)

        self._building_div = None

    @property
    def building_div(self):
        if self._building_div is None:
            self.refresh()
        return self._building_div

    def get_text_sprite(self, txt):
        return UIElement(self.FONT.render(txt, True, 'black').convert_alpha())

    @property
    def capacity_descriptor(self):
        pm = self.building.production_method
        job_descs_div = Div(False, 10)
        for job in pm.job_capacity_demand_per_level:
            # Key stats
            job_max_demand = int(pm.job_capacity_demand_per_level[job] * pm.level)
            job_supply = int(pm.get_total_job_capacity_supply(job))
            fulfillment = round(job_supply / job_max_demand * 100, 1)

            # Job description
            job_desc = Div(False, 5)
            desc = f"{job.name.title()}: {job_supply} / {job_max_demand} ({fulfillment}%)"
            job_desc.add_sprites(self.get_text_sprite(desc))

            for worker in pm.workforce[job]:
                if pm.workforce[job][worker] > 0:
                    worker_desc_div = Div(True, center=True)
                    worker_desc_div.add_sprites(self.get_text_sprite("--"))

                    worker_image = UIElement(load_image(WORKER_MANAGERS[worker].image_loc, self.UNIT_ICON_SIZE))
                    worker_desc_div.add_sprites(worker_image)

                    contribution_percentage = pm.total_capacity_from_worker_for_job(worker, job) / job_supply
                    workforce_desc = (
                        f"x {pm.workforce[job][worker]} "
                        f"({contribution_percentage * 100:.0f}% of capacity)"
                    )
                    worker_desc_div.add_sprites(self.get_text_sprite(workforce_desc))
                    # job_desc.add_surface(self.get_text_sprite(workforce_desc))
                    job_desc.add_div(worker_desc_div)
            job_descs_div.add_div(job_desc)

        return job_descs_div

    @property
    def military_input_descriptor(self):
        pm = self.building.production_method

        if type(pm)!=MilitaryProductionMethod:
            return None
        else:
            job_desc = Div(False)
            job_desc.add_sprites(self.get_text_sprite("Soldiers:"))
            soldiers_div = Div()
            soldiers_div.add_sprites(self.get_text_sprite("--"))
            soldiers_div.add_sprites(UIElement(load_image(WORKER_MANAGERS[pm.input_worker].image_loc, self.UNIT_ICON_SIZE)))
            soldiers_div.add_sprites(self.get_text_sprite(f"x {pm.active_soldiers}"))
            job_desc.add_div(soldiers_div)
            return job_desc

    @property
    def military_output_descriptor(self):
        pm = self.building.production_method
        if type(pm) != MilitaryProductionMethod:
            return None
        else:
            soldiers_div = Div()
            soldiers_div.add_sprites(
                UIElement(load_image(MINION_TO_STATS[pm.output_soldier].image_loc, self.UNIT_ICON_SIZE))
            )
            soldiers_div.add_sprites(self.get_text_sprite(f"x {pm.active_soldiers}"))
            return soldiers_div


    def _generate_goods_descriptor(self, goods_dict: Dict[Good, float]) -> Div:
        goods_descs_div = Div(False, 10)
        for good in goods_dict:
            if goods_dict[good] > 0:
                good_desc_div = Div(True, 5)
                good_desc_div.add_sprites(UIElement(load_image(GOOD_STATS[good].image_loc, (30,30))))
                good_desc_div.add_sprites(self.get_text_sprite(str(int(goods_dict[good]))))
                goods_descs_div.add_div(good_desc_div)
        return goods_descs_div

    @property
    def good_consumption_descriptor(self) -> Div:
        return self._generate_goods_descriptor(self.building.production_method.input_goods_demand)

    @property
    def good_production_descriptor(self) -> Div:
        return self._generate_goods_descriptor(self.building.production_method.output_goods_supply)


    def refresh(self):

        # Get title div
        title_div = Div(True)

        # Building image
        title_div.add_sprites(UIElement(self.building_icon))

        # Building desc
        description_div = Div(False)
        description_div.add_sprites(UIElement(self.title))
        description_div.add_sprites(self.get_text_sprite(f"Num levels: {self.building.production_method.level}"))
        title_div.add_div(description_div)

        if self.add_soldier_button:
            # title_div.add_sprites(self.add_soldier_button)
            title_div.add_sprites(self.add_soldier_button)

        # Production Method
        production_method_div = Div(True, center=True)

        # -- Inputs
        inputs_div = Div(False)
        if len(self.capacity_descriptor.ordered_elements)>0:
            inputs_div.add_div(self.capacity_descriptor)
        if len(self.good_consumption_descriptor.ordered_elements)>0:
            inputs_div.add_div(self.good_consumption_descriptor)
        if self.military_input_descriptor:
            inputs_div.add_div(self.military_input_descriptor)
        if len(inputs_div.ordered_elements)>0:
            production_method_div.add_div(inputs_div)

        # -- Arrow
        production_method_div.add_sprites(UIElement(BuildingEntry.ARROW_SURFACE))

        # -- Outputs
        outputs_div = Div(False)
        if len(self.good_production_descriptor.ordered_elements)>0:
            outputs_div.add_div(self.good_production_descriptor)
        if self.add_soldier_button:
            outputs_div.add_div(self.military_output_descriptor)

        production_method_div.add_div(outputs_div)

        # Production method
        building_div = Div(False, 20, background_color="silver", min_width=int(WIDTH/3))
        building_div.add_div(title_div)
        building_div.add_div(production_method_div)

        self._building_div = building_div

        # if self.add_soldier_button:
        #     print(self._building_div.rect.width)


class BuildingUI:
    PAPYRUS_COLOR = (235, 213, 179)
    TITLE_FONT = pygame.font.SysFont('arial', 30)


    def __init__(self, title: str, topleft: Tuple[int, int]):

        self.topleft = topleft
        self.image = None
        self.rect = None

        self.title = self.TITLE_FONT.render(title, True, "black").convert_alpha()


        self.building_entries: List[BuildingEntry] = []
        self.add_soldier_buttons: List[AddSoldierButton] = []
        self.should_display = False

        self.sprites = []

        self.compile()

    def add_building(self, building: Building):
        building_entry = BuildingEntry(building)
        self.building_entries.append(building_entry)
        if building_entry.add_soldier_button:
            self.add_soldier_buttons.append(building_entry.add_soldier_button)


    def compile(self):
        ui_div = Div(False, 20, background_color=self.PAPYRUS_COLOR, center=True)
        ui_div.add_sprites(UIElement(self.title))
        for building_entry in self.building_entries:
            building_entry.refresh()
            ui_div.add_div(building_entry.building_div)

        # Register all child sprites
        self.sprites = ui_div.get_all_descendants_with_offset(self.topleft)

        self.rect = pygame.Rect(*self.topleft,0,0)
        for s in self.sprites:
            self.rect.union_ip(s.rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.fill(self.PAPYRUS_COLOR)


    def toggle_on(self):
        self.should_display = True

    def toggle_off(self):
        self.should_display = False

    def draw(self, surface: pygame.Surface):
        for sprite in self.sprites:
            surface.blit(sprite.image, sprite.rect)
        for button in self.add_soldier_buttons:
            if button.is_hovered:
                pygame.draw.rect(surface, "red", button.rect, 3)

# e = load_image("elf.png", (30,30))
# d = Div(True)
# d.add_sprites(UIElement(e))
# d.add_sprites(UIElement(e))
# d.add_sprites(UIElement(e))
# d.add_sprites(UIElement(e))
#
#
# d2 = Div(True)
# d2.add_sprites(UIElement(e))
# d2.add_sprites(UIElement(e))
# d2.add_sprites(UIElement(e))
# d2.add_sprites(UIElement(e))
#
# d3 = Div(False)
# d3.add_div(d)
# d3.add_div(d2)
# descs = d3.get_all_descendants_with_offset((2,2))
# print("Bonjour :)")
# for desc in descs:
#     print(desc.rect)

if __name__ == "__main__":
    screen.fill("white")

    clock = pygame.time.Clock()
    building_ui = BuildingUI("Buildings Registry", (10,10))
    building_ui.add_building(Building("Building", "orc_settlement.png", standard_woodcutting))
    building_ui.compile()
    running = True
    while running:
        screen.fill("white")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        building_ui.draw(screen)
        # for desc in descs:
        #     screen.blit(desc.image, desc.rect)
        pygame.display.update()



