from collections import Counter

# from economy.tracker_base_class import Tracker
from goods import Good,  GoodStats
from dataclasses import dataclass

# from economy.economy_base_classes import
from economy.worker import Job, Worker, get_worker_manager
from typing import List, Dict

from copy import deepcopy

from utils import multiply_dict_by_value, add_dicts, diff_dicts


@dataclass
class ProductionMethod:
    """
    Class to track a productino method, both
    """

    job_capacity_demand_per_level: Dict[Job, float]
    good_consumption: Dict[Good, float]
    good_production: Dict[Good, float]
    level: int = 0

    def __post_init__(self):
        self.workforce: Dict[Job, Counter[Worker]] = {
            job: Counter() for job in self.job_capacity_demand_per_level
        }

    def add_levels(self, levels: int):
        self.level += levels

    def remove_levels(self, levels: int):
        self.level = max(0, self.level - levels)

    def get_total_job_capacity_supply(self, job: Job) -> float:
        capacity = 0
        if job in self.job_capacity_demand_per_level:
            job_workers = self.workforce[job]
            for worker_type in job_workers:
                capacity += get_worker_manager(worker_type).get_capacity(job) * job_workers[worker_type]
        return capacity

    @property
    def job_fulfillment(self) -> Dict[Job, float]:
        """
        Returns a dictionary that maps jobs to the proportion of the maximum demand for said job that is fulfilled.
        :return:
        """
        _job_fulfillment = {}
        for job in self.job_capacity_demand_per_level:
            _job_fulfillment[job] = self.get_total_job_capacity_supply(job) / (self.job_capacity_demand_per_level[job] * self.level)
        return _job_fulfillment

    @staticmethod
    def get_key_of_min_value(d: Dict):
        return min(d, key=d.get)

    @property
    def job_bottleneck(self) -> Job:
        return self.get_key_of_min_value(self.job_fulfillment)

    def shortage_jobs(self, shortage_diff: float = 0.1) -> List[Job]:
        """
        Once employment gets to an acceptable point, only jobs that are significantly behind the top job
        count as being in shortage.
        """
        job_fulfillment = self.job_fulfillment
        best_fulfillment = max(job_fulfillment.values())
        if best_fulfillment > shortage_diff:
            shortage_fulfillment_threshold = best_fulfillment - shortage_diff
            return [job for job in job_fulfillment if job_fulfillment[job]<shortage_fulfillment_threshold]
        else:
            return []



    @property
    def job_labour_fulfillment(self) -> float:
        return min(self.job_fulfillment.values())

    @property
    def input_goods_demand(self) -> dict[Good, float]:
        return multiply_dict_by_value(self.good_consumption, self.job_labour_fulfillment*self.level)

    @property
    def output_goods_supply(self) -> dict[Good, float]:
        return multiply_dict_by_value(self.good_production, self.job_labour_fulfillment*self.level)

    @property
    def overall_market_impact(self):
        return diff_dicts(self.output_goods_supply, self.input_goods_demand)

    def evaluate_impact_of_capacity_reduction(self, worker: Worker, job: Job, num_workers: int = 1) -> Dict[Good, float]:
        simulated_production_method = deepcopy(self)
        simulated_production_method.remove_workers(worker, job, num_workers)
        goods_difference = diff_dicts(simulated_production_method.overall_market_impact, self.overall_market_impact)
        return goods_difference

    def evaluate_impact_of_capacity_increase(self, worker: Worker, job: Job, num_workers: int = 1) -> Dict[Good, float]:
        simulated_production_method = deepcopy(self)
        simulated_production_method.add_workers(worker, job, num_workers)
        goods_difference = diff_dicts(simulated_production_method.overall_market_impact, self.overall_market_impact)
        # print(goods_difference)
        return goods_difference


    def max_productivity_estimate_of_capacity_increase(self, worker: Worker, job: Job) -> Dict[Good, float]:
        capacity_increase = min(get_worker_manager(worker).get_capacity(job), self.potential_capacity_remaining(job))
        demand_for_job_fulfillment_increase = capacity_increase / (self.job_capacity_demand_per_level[job] * self.level)
        return multiply_dict_by_value(self.overall_market_impact, demand_for_job_fulfillment_increase)

    def potential_capacity_remaining(self, job: Job) -> float:
        return self.job_capacity_demand_per_level[job]*self.level-self.get_total_job_capacity_supply(job)

    def has_capacity_for_worker_job(self, worker: Worker, job: Job) -> bool:
        worker_capacity = get_worker_manager(worker).get_job_capacity(job)
        if job in self.job_capacity_demand_per_level:
            return self.potential_capacity_remaining(job) >= worker_capacity
        else:
            return False

    # def capacity_usage_of_worker_job(self, worker: Worker, job: Job) -> float:
    #     worker_capacity = get_worker_manager(worker).get_job_capacity(job)
    #

    def jobs_with_capacity_for_worker(self, worker: Worker) -> List[Job]:
        jobs_with_capacity = []
        for job in self.job_capacity_demand_per_level:
            if self.has_capacity_for_worker_job(worker, job):
                jobs_with_capacity.append(job)
        return jobs_with_capacity

    def add_workers(self, worker: Worker, job: Job, num: int):
        total_added_capacity = num * get_worker_manager(worker).get_capacity(job)
        if total_added_capacity > self.potential_capacity_remaining(job):
            raise ValueError(f"Tried to add {total_added_capacity} of {job} capacity but the maximum remaining is {self.potential_capacity_remaining(job)}")
        else:
            self.workforce[job][worker] += num

    def max_capacity_remaining_for_worker_job(self, worker: Worker, job: Job) -> int:
        return int(self.potential_capacity_remaining(job)/get_worker_manager(worker).get_capacity(job))

    def remove_workers(self, worker: Worker, job: Job, num: int):
        if num>self.workforce[job][worker]:
            raise ValueError(f"Cannot remove {num} of {worker} from {job} (more than current assigned {self.workforce[job][worker]})")
        self.workforce[job][worker] = max(0, self.workforce[job][worker] - num)



class Building:
    def __init__(self, production_method: ProductionMethod, max_levels: int = 0):
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
        actual_expansion = min(num_levels, self.max_levels-self.production_method.level)
        self.production_method.add_levels(actual_expansion)

    def reduce_production_method(self, num_levels: int):
        self.validate_level_value(num_levels)
        actual_reduction = min(self.production_method.level, num_levels)
        self.production_method.remove_levels(actual_reduction)


standard_woodcutting = ProductionMethod(
    job_capacity_demand_per_level={Job.WOODCUTTING: 10, Job.FARMING: 5},
    good_consumption={},
    good_production={Good.WOOD: 10, Good.MEAT: 5, Good.GRAIN: 4},
    level=5,
)

if __name__ == "__main__":
    elf = Worker.ELF
    # standard_woodcutting.add_workers(elf, Job.WOODCUTTING, 10)

    print(standard_woodcutting.get_total_job_capacity_supply(Job.WOODCUTTING))

    Woods = Building(standard_woodcutting, 20)