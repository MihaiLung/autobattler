import sys

import pygame

from economy.buildings import ProductionMethod, Building
from economy.economy_manager import standard_farming
from economy.worker import Worker, Job
from settings import WIDTH, HEIGHT
from utils import load_image, bound_rect_within_screen
from typing import Union, Optional

dummy_pm = standard_farming
dummy_pm.add_workers(Worker.ORC, Job.WOODCUTTING, 10)
dummy_pm.add_workers(Worker.ELF, Job.FARMING, 15)
dummy_pm.add_workers(Worker.ELF, Job.WOODCUTTING, 20)

dummy_building = Building("Dummy Building", "orc_settlement.png", dummy_pm)

class UIElement(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

class Div:
    def __init__(
            self,
            horizontal: bool=True,
            margin_between_elements: int = 10,
            background_color = None,
            min_width: Optional[int] = None,
        ):
        self.ordered_elements = []
        self.horizontal = horizontal
        self.margin_between_elements = margin_between_elements
        self.background_color = background_color
        self.min_width = min_width


    def add_surface(self, element: pygame.Surface):
        self.ordered_elements.append(UIElement(element))

    def add_div(self, element: 'Div'):
        self.ordered_elements.append(element.compile_div())

    def compile_div(self) -> UIElement:
        if self.horizontal:
            margin_computation = lambda previous_rect: (previous_rect.right + self.margin_between_elements, 0)
        else:
            margin_computation = lambda previous_rect: (0, previous_rect.bottom+self.margin_between_elements)

        overall_rect = self.ordered_elements[0].rect.copy()
        for previous_element, element in zip(self.ordered_elements[:-1], self.ordered_elements[1:]):
            element.rect.move_ip(margin_computation(previous_element.rect))
            overall_rect.union_ip(element.rect)


        if self.min_width and self.min_width>0:
            overall_rect.width = max(self.min_width, overall_rect.width)
        image = pygame.Surface(overall_rect.size, pygame.SRCALPHA)
        if self.background_color:
            image.fill(self.background_color)
        for element in self.ordered_elements:
            image.blit(element.image, element.rect)
        return UIElement(image)



class BuildingEntry(pygame.sprite.Sprite):
    FONT = pygame.font.SysFont('timesnewroman', 18)
    TITLE_FONT = pygame.font.SysFont('timesnewroman', 20, bold=True)
    def __init__(self, building: Building):
        pygame.sprite.Sprite.__init__(self)
        self.building = building
        self.building_icon = load_image(building.image_loc)
        self.building_icon = pygame.transform.smoothscale(self.building_icon, (50,50))
        self.building_icon_rect = self.building_icon.get_rect()
        self.title = self.TITLE_FONT.render(building.name.title(), True, 'black').convert_alpha()

        self.image = None
        self.rect = None

        self.refresh()

    def get_text_sprite(self, txt):
        print(txt)
        return self.FONT.render(txt, True, 'black').convert_alpha()

    def get_capacity_descriptors(self):
        pm = self.building.production_method
        job_descs = Div(False, 10)
        for job in pm.job_capacity_demand_per_level:
            job_desc = Div(False, 5)

            job_max_demand = int(pm.job_capacity_demand_per_level[job] * pm.level)
            job_supply = int(pm.get_total_job_capacity_supply(job))
            fulfillment = round(job_supply / job_max_demand * 100, 1)

            desc = f"{job.name.title()}: {job_supply} / {job_max_demand} ({fulfillment}%)"
            job_desc.add_surface(self.get_text_sprite(desc))

            for worker in pm.workforce[job]:
                if pm.workforce[job][worker] > 0:
                    contribution_percentage = pm.total_capacity_from_worker_for_job(worker, job) / job_supply
                    workforce_desc = (
                        f" -- {worker.name.title()} x {pm.workforce[job][worker]} "
                        f"({contribution_percentage * 100:.0f}% of capacity)"
                    )
                    job_desc.add_surface(self.get_text_sprite(workforce_desc))
            job_descs.add_div(job_desc)

        return job_descs


    def refresh(self):

        title_div = Div(True)
        title_div.add_surface(self.building_icon)

        description_div = Div(False)
        description_div.add_surface(self.title)
        description_div.add_surface(self.get_text_sprite(f"Num levels: {self.building.production_method.level}"))

        title_div.add_div(description_div)

        building_div = Div(False, 20, background_color="silver", min_width=int(WIDTH/3))
        building_div.add_div(title_div)
        building_div.add_div(self.get_capacity_descriptors())

        self.image = building_div.compile_div().image
        self.rect = self.image.get_rect()

    def get_surface(self):
        if not self.image:
            self.refresh()
        return self.image


    def draw(self, surface: pygame.Surface, y_offset: int = 0):
        surface.blit(self.image, self.rect.move(0, y_offset))



class BuildingUI(pygame.sprite.Sprite):
    PAPYRUS_COLOR = (235, 213, 179)
    TITLE_FONT = pygame.font.SysFont('timesnewroman', 30)

    def __init__(self, title):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH/3, HEIGHT*0.8))
        self.rect = self.image.get_rect()
        self.image.fill(self.PAPYRUS_COLOR)

        self.title = self.TITLE_FONT.render(title, True, "black")
        title_rect = self.title.get_rect()
        title_rect.midtop = int(self.rect.width/2), 0
        self.image.blit(self.title, title_rect)


        self.building_entries = []
        self.should_display = False

    def add_building(self, building: Building):
        self.building_entries.append(BuildingEntry(building))


    def refresh(self):
        ui_div = Div(False, 30, background_color=self.PAPYRUS_COLOR)
        ui_div.add_surface(self.title)
        for building_entry in self.building_entries:
            building_entry.refresh()
            ui_div.add_surface(building_entry.image)

        compiled_ui = ui_div.compile_div()
        self.image = compiled_ui.image
        self.rect = compiled_ui.rect.move(50, 80)


    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_at_mouse_pos(self, screen):
        self.rect.midtop = pygame.mouse.get_pos()
        self.rect = bound_rect_within_screen(self.rect, screen)
        self.draw(screen)

    def toggle_on(self):
        self.should_display = True

    def toggle_off(self):
        self.should_display = False


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Building UI")
    clock = pygame.time.Clock()
    building_ui = BuildingUI("Buildings Registry")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        building_ui.draw(screen)
        pygame.display.update()

