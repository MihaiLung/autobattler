from economy.goods import Good
from economy.production_methods.economic_production_method import ProductionMethod
from economy.production_methods.military_production_method import MilitaryProductionMethod
from economy.worker import Job, Worker

from typing import Union

example_woodcutting = ProductionMethod(
    job_capacity_demand_per_level={Job.WOODCUTTING: 10, Job.FARMING: 5, Job.MAGIC: 1},
    good_consumption_per_level={},
    good_production_per_level={Good.WOOD: 10, Good.MEAT: 5, Good.GRAIN: 4},
    starting_levels=5,
)


class Building:
    def __init__(self, name: str, image_loc: str, production_method: Union[ProductionMethod, MilitaryProductionMethod], max_levels: int = 0):
        self.name = name
        self.image_loc = image_loc
        self.production_method = production_method
        self.max_levels = max_levels

    def add_levels(self, additional_levels: int):
        self.max_levels = max(0, self.max_levels+additional_levels)

    @staticmethod
    def validate_level_value(num_levels: int):
        if num_levels < 1:
            raise ValueError("num_levels must be a positive integer")

    def expand_production_method(self, num_levels: int):
        self.validate_level_value(num_levels)
        actual_expansion = min(num_levels, self.max_levels - self.production_method.level)
        self.production_method.add_levels(actual_expansion)

    def reduce_production_method(self, num_levels: int):
        self.validate_level_value(num_levels)
        actual_reduction = min(self.production_method.level, num_levels)
        self.production_method.remove_levels(actual_reduction)


if __name__ == "__main__":
    elf = Worker.ELF
    # standard_woodcutting.add_workers(elf, Job.WOODCUTTING, 10)

    # print(standard_woodcutting.get_total_job_capacity_supply(Job.WOODCUTTING))

    Woods = Building("Orc City", "orc_city.png", example_woodcutting, 20)