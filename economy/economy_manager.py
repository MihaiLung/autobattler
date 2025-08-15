from collections import Counter

from battle_logic.character_settings.minion_base_class import MinionStats
from battle_logic.character_settings.minion_stats import Minion
from economy.production_methods.economic_production_method import ProductionMethod
from economy.buildings import Building
from economy.goods import Marketplace, Good
from typing import List, Dict, Tuple

from economy.production_methods.military_production_method import MilitaryProductionMethod
from economy.worker import Worker, Job, get_worker_manager
from utils import multiply_dict_by_value, add_dicts

from dataclasses import dataclass
import time

@dataclass
class WorkEvaluation:
    worker: Worker
    job: Job
    building: Building
    value: float

    def apply_assignment(self):
        self.building.production_method.add_workers(self.worker, self.job, 1)

    def __str__(self):
        return f"WorkEvaluation(worker={self.worker}, job={self.job}, value={self.value})"

@dataclass
class ProfitEvaluation:
    full_productivity: float
    actual: float

    @property
    def opportunity_value(self) -> float:
        return self.actual*0.98 + self.full_productivity*0.00002

class EconomyManager:
    def __init__(self, buildings: List[Building], workers: Counter[Worker]):
        self.market = Marketplace()
        self.buildings = buildings
        self.unemployed_workers = workers

        self._allocate_initial_workforce()
        self.refresh_market()

    @property
    def capacity_usage_potentials(self) -> Dict[Job, float]:
        d_capacity_usage_potentials = {}
        for building in self.buildings:
            building_potentials = multiply_dict_by_value(
                building.production_method.job_capacity_demand_per_level,
                building.production_method.level
            )
            d_capacity_usage_potentials = add_dicts(d_capacity_usage_potentials, building_potentials)
        return d_capacity_usage_potentials

    @staticmethod
    def most_suitable_worker(workers: List[Worker], job: Job) -> Worker:
        return max(workers, key=lambda w: get_worker_manager(w).get_job_capacity(job))

    def _allocate_initial_workforce(self, num_workers_per_job: int = 2):
        """
        Allocates a given number of workers to each job where possible. Meant to kickstart the economy.
        """
        for building in self.buildings:
            for job in building.production_method.job_capacity_demand_per_level:
                worker = self.most_suitable_worker(workers=list(self.unemployed_workers.keys()), job=job)
                remaining_workers = self.unemployed_workers[worker]
                max_capacity_remaining = building.production_method.max_capacity_remaining_for_worker_job(worker, job)
                actual_addition = min(num_workers_per_job, remaining_workers, max_capacity_remaining)
                building.production_method.add_workers(worker, job, actual_addition)
                self.unemployed_workers[worker] -= actual_addition

    @property
    def worker_counts(self) -> Counter[Worker]:
        all_workers = self.unemployed_workers.copy()
        for building in self.buildings:
            workforce = building.production_method.workforce
            for job in workforce:
                all_workers += workforce[job]
        return all_workers


    def evaluate_impact_of_removing_worker_from_job(self, worker: Worker, job: Job, building: Building) -> float:
        """
        Evaluates how much revenue a worker generates in their current job. Ignores costs.
        """
        incremental_goods_impact = building.production_method.evaluate_impact_of_capacity_reduction(
            worker=worker,
            job=job,
            num_workers=1
        )
        # This is the LOSS in value should the worker lose this job. So the worker's current contribution is the reverse of this
        value_of_goods_lost = self.market.value_goods_package(incremental_goods_impact)
        return value_of_goods_lost

    def evaluate_impact_of_adding_worker_to_job(self, worker: Worker, job: Job, building: Building) -> ProfitEvaluation:
        full_productivity_incremental_goods_impact = building.production_method.max_productivity_estimate_of_capacity_increase(
            worker=worker,
            job=job,
        )
        full_productivity_value_of_goods_added = self.market.value_goods_package(full_productivity_incremental_goods_impact)

        actual_incremental_goods_impact = building.production_method.evaluate_impact_of_capacity_increase(
            worker=worker,
            job=job,
        )
        actual_value_of_goods_added = self.market.value_goods_package(actual_incremental_goods_impact)


        return ProfitEvaluation(actual=actual_value_of_goods_added, full_productivity=full_productivity_value_of_goods_added)

    def evaluate_worker_opportunities(self, worker: Worker) -> Dict[Building, Dict[Job, ProfitEvaluation]]:
        d_opportunities = {}
        for building in self.buildings:
            d_opportunities[building] = {}
            for job in building.production_method.jobs_with_capacity_for_worker(worker):
                d_opportunities[building][job] = self.evaluate_impact_of_adding_worker_to_job(worker, job, building)
        return d_opportunities

    def unassign_worker(self, worker: Worker):
        found_worker = False
        if self.unemployed_workers[worker]>0:
            self.unemployed_workers[worker]-=1
            found_worker = True
        else:
            for building in self.buildings:
                for job in building.production_method.workforce:
                    if building.production_method.workforce[job][worker]>0:
                        building.production_method.workforce[job][worker]-=1
                        found_worker = True
                        break
        if not found_worker:
            raise ValueError(f"Tried unassigning a worker of race {worker.name} but none available")



    @property
    def shortage_buildings(self) -> List[Building]:
        shortage_buildings = []
        for building in self.buildings:
            if len(building.production_method.shortage_jobs()) > 0:
                shortage_buildings.append(building)
        return shortage_buildings

    def best_opportunity_for_worker(self, worker: Worker) -> WorkEvaluation:
        d_opportunities = self.evaluate_worker_opportunities(worker=worker)
        # print("Opportunities evaluations")
        # for building in d_opportunities:
            # for job in d_opportunities[building]:
                # print(f"-- {job} -- {d_opportunities[building][job]}")
        best_opportunity_value = 0.
        most_profitable_opportunity = None
        for building in d_opportunities:
            possible_jobs = building.production_method.jobs_with_capacity_for_worker(worker=worker)
            shortage_jobs = building.production_method.shortage_jobs()
            if len(shortage_jobs) > 0:
                search_jobs = shortage_jobs
            else:
                search_jobs = possible_jobs
            # print(f"Search jobs were: {search_jobs}")
            for job in search_jobs:
                opportunity_value = d_opportunities[building][job].opportunity_value
                if opportunity_value > best_opportunity_value:
                    best_opportunity_value = opportunity_value
                    most_profitable_opportunity = WorkEvaluation(
                        worker=worker,
                        job=job,
                        building=building,
                        value=d_opportunities[building][job].opportunity_value,
                    )
        return most_profitable_opportunity

    def refresh_market(self):
        # Update marketplace with demand and supply
        self.market = Marketplace()
        for worker in self.worker_counts:

            self.market.add_demand(multiply_dict_by_value(get_worker_manager(worker).sustenance_goods, self.worker_counts[worker]))

        for building in self.buildings:
            production_method = building.production_method
            self.market.add_demand(production_method.input_goods_demand)
            self.market.add_supply(production_method.output_goods_supply)


    def tick_economy(self):
        self.refresh_market()

        # Assign unemployed workers
        num_worker_assignments_per_tick = 2
        for i in range(num_worker_assignments_per_tick):
            worker_opportunites = []
            # print("="*20)
            # print("Opportunities at step ", i)

            if sum(self.unemployed_workers.values())>0:
                for worker in self.unemployed_workers:
                    # print(f"For worker {worker}:")
                    if self.unemployed_workers[worker]>0:
                        most_profitable_opportunity = self.best_opportunity_for_worker(worker=worker)
                        if most_profitable_opportunity is not None:
                            worker_opportunites.append(most_profitable_opportunity)
                    # print(f"Best opportunity: {most_profitable_opportunity}")
                    # print()

                if len(worker_opportunites)>0:
                    best_assignment = max(worker_opportunites, key=lambda w: w.value)
                    if type(best_assignment) is WorkEvaluation:
                        best_assignment.apply_assignment()
                        # print(f"Opportunity assigned to worker {best_assignment.worker} for job {best_assignment.job}")
                        self.unemployed_workers[best_assignment.worker] -= 1

                    # print(f"Job fulfillment: {self.buildings[0].production_method.job_fulfillment}")
                    # print(f"Market demand: {self.market.demand}")
                    # print(f"Market supply: {self.market.supply}")
                    # print("="*20)
                    # print("\n")


standard_woodcutting = ProductionMethod(
    job_capacity_demand_per_level={Job.WOODCUTTING: 20},
    good_consumption_per_level={},
    good_production_per_level={Good.WOOD: 3, Good.MEAT: 10},
    starting_levels=50,
)

standard_farming = ProductionMethod(
    job_capacity_demand_per_level={Job.FARMING: 10},
    good_consumption_per_level={Good.WOOD: 1},
    good_production_per_level={Good.GRAIN: 8},
    starting_levels=50,
)

elven_military = MilitaryProductionMethod(
    job_capacity_demand_per_level={},
    good_consumption_per_level={Good.WOOD: 1},
    good_production_per_level={},
    input_worker=Worker.ELF,
    output_soldier=Minion.RANGER,
    starting_level=60
)


buildings = [
    Building("Lumber Mills", "orc_settlement.png", standard_woodcutting),
    Building("Farms", "elf_settlement.png", standard_farming),
    Building("Elven Barracks", "elf.png", elven_military),
]
workers = Counter({
    Worker.ORC: 40,
    Worker.ELF: 100
})
economy_manager = EconomyManager(buildings=buildings, workers=workers)

if __name__ == '__main__':
    economy_manager.tick_economy()
    for i in range(100):
        print(f"Tick {i}")
        economy_manager.tick_economy()