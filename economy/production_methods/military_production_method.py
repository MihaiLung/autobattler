from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List

from battle_logic.character import Character
from battle_logic.character_settings.minion_stats import Minion
from economy.goods import Good
from economy.production_methods.economic_production_method import ProductionMethod
from economy.worker import Job, Worker, get_worker_manager
from utils import multiply_dict_by_value, diff_dicts


class MilitaryProductionMethod(ProductionMethod):
    """
    Special class for military production methods. Inherits from ProductionMethod since in many ways it works the same,
    but the extra stuff it needs to do is complex enough to warrant separate treatment.
    """

    def __init__(
            self,
            job_capacity_demand_per_level: Dict[Job, float], # For soldiers this is support jobs (if any); not the soldiers themselves!
            good_consumption_per_level: Dict[Good, float],
            good_production_per_level: Dict[Good, float],
            input_worker: Worker,
            output_soldier: Minion,
            num_soldiers_per_level: int = 1,
            starting_level: int = 0,
    ):
        super().__init__(job_capacity_demand_per_level, good_consumption_per_level, good_production_per_level, starting_level)
        self.input_worker = input_worker
        self.output_soldier = output_soldier
        self.num_soldiers_per_level = num_soldiers_per_level
        self.active_soldiers: int = 0

    @property
    def job_labour_fulfillment(self) -> float:
        return self.active_soldiers / self.num_soldiers_needed_for_full_capacity

    @property
    def num_soldiers_needed_for_full_capacity(self) -> int:
        return self.level - self.active_soldiers

    def add_soldiers(self, num_soldiers: int):
        if num_soldiers >= self.num_soldiers_needed_for_full_capacity:
            raise ValueError(f"Tried adding {num_soldiers} soldiers but the max capacity is {self.num_soldiers_needed_for_full_capacity}!")
        if num_soldiers < 0:
            raise ValueError("Provided number of soldiers cannot be negative!")
        self.active_soldiers += num_soldiers

    def remove_soldiers(self, num_soldiers: int):
        if num_soldiers > self.active_soldiers:
            raise ValueError(f"Tried removing {num_soldiers} soldiers but only {self.active_soldiers} available!")
        if num_soldiers < 0:
            raise ValueError("Provided number of soldiers cannot be negative!")
        self.active_soldiers -= num_soldiers




if __name__ == "__main__":
    dummy_pm = MilitaryProductionMethod(
        job_capacity_demand_per_level={

        },
        good_consumption_per_level={},
    )