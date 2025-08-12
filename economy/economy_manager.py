from collections import Counter

from economy.buildings import Building, ProductionMethod, standard_woodcutting
from economy.goods import Marketplace, Good
from typing import List, Dict, Tuple

from economy.worker import Worker, Job, get_worker_manager
from utils import multiply_dict_by_value, add_dicts

from dataclasses import dataclass

@dataclass
class WorkEvaluation:
    worker: Worker
    job: Job
    building: Building
    value: float

    def apply_assignment(self):
        self.building.production_method.add_workers(self.worker, self.job, 1)

@dataclass
class ProfitEvaluation:
    full_productivity: float
    actual: float

    @property
    def opportunity_value(self) -> float:
        return self.actual*0.7 + self.full_productivity*0.3

class EconomyManager:
    def __init__(self, buildings: List[Building], workers: Counter[Worker]):
        self.market = Marketplace()
        self.buildings = buildings
        self.unemployed_workers = workers

        self._allocate_initial_workforce()

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
        return max(workers, key=lambda w: get_worker_manager(w).get_capacity(job))

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
            for job in building.production_method.job_capacity_demand_per_level:
                d_opportunities[building][job] = self.evaluate_impact_of_adding_worker_to_job(worker, job, building)
        return d_opportunities

    @property
    def shortage_buildings(self) -> List[Building]:
        shortage_buildings = []
        for building in self.buildings:
            if len(building.production_method.shortage_jobs()) > 0:
                shortage_buildings.append(building)
        return shortage_buildings

    def best_opportunity_for_worker(self, worker: Worker) -> WorkEvaluation:
        d_opportunities = self.evaluate_worker_opportunities(worker=worker)
        best_opportunity_value = 0.
        most_profitable_opportunity = None
        for building in d_opportunities:
            # shortage_jobs = building.production_method.shortage_jobs()
            for job in d_opportunities[building]:
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


    def tick_economy(self):
        # Update marketplace with demand and supply
        marketplace = Marketplace()
        for worker in self.worker_counts:
            marketplace.add_demand(multiply_dict_by_value(get_worker_manager(worker).sustenance_goods, self.worker_counts[worker]))
        for building in self.buildings:
            production_method = building.production_method
            marketplace.add_demand(production_method.input_goods_demand)
            marketplace.add_supply(production_method.output_goods_supply)

        # Assign unemployed workers
        num_worker_assignments_per_tick = 50
        for i in range(num_worker_assignments_per_tick):
            worker_opportunites = []
            for worker in self.unemployed_workers:
                if self.unemployed_workers[worker]>0:
                    most_profitable_opportunity = self.best_opportunity_for_worker(worker=worker)
                    if most_profitable_opportunity is not None:
                        worker_opportunites.append(most_profitable_opportunity)
            best_assignment = max(worker_opportunites, key=lambda w: w.value)
            if type(best_assignment) is WorkEvaluation:
                print("-"*10)
                print(self.worker_counts)
                print("before")
                print(best_assignment.building.production_method.workforce)
                best_assignment.apply_assignment()
                self.unemployed_workers[best_assignment.worker] -= 1
                print("after")
                print(best_assignment.building.production_method.workforce)
                print("-"*10)



if __name__ == '__main__':
    standard_woodcutting = ProductionMethod(
        job_capacity_demand_per_level={Job.WOODCUTTING: 10, Job.FARMING: 5},
        good_consumption={},
        good_production={Good.WOOD: 10, Good.MEAT: 5, Good.GRAIN: 4},
        level=50,
    )

    buildings = [
        Building(standard_woodcutting)
    ]
    workers = Counter({
        Worker.ORC: 10,
        Worker.ELF: 100
    })
    manager = EconomyManager(buildings=buildings, workers=workers)
    manager.tick_economy()

    summary_dict = {}
    for job in buildings[0].production_method.workforce:
        summary_dict[job.name] = {}
        job_workforce = buildings[0].production_method.workforce[job]
        for worker in job_workforce:
            summary_dict[job.name][worker.name] = job_workforce[worker]
    print(summary_dict)
    print(manager.unemployed_workers)
    print(manager.worker_counts)

