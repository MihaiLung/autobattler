from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List

from economy.goods import Good
from economy.worker import Job, Worker, get_worker_manager
from utils import multiply_dict_by_value, diff_dicts


# @dataclass
class ProductionMethod:
    """
    Class to track a productino method, both
    """

    # job_capacity_demand_per_level: Dict[Job, float]
    # good_consumption: Dict[Good, float]
    # good_production: Dict[Good, float]
    # level: int = 0

    def __init__(
            self,
            job_capacity_demand_per_level: Dict[Job, float],
            good_consumption_per_level: Dict[Good, float],
            good_production_per_level: Dict[Good, float],
            starting_levels: int = 0
    ):
        self.job_capacity_demand_per_level = job_capacity_demand_per_level
        self.good_consumption_per_level = good_consumption_per_level
        self.good_production_per_level = good_production_per_level
        self.level = starting_levels
        self.workforce: Dict[Job, Counter[Worker]] = {
            job: Counter() for job in self.job_capacity_demand_per_level
        }

        self.uses_labour = len(job_capacity_demand_per_level)>0


    def add_levels(self, levels: int):
        self.level += levels

    def remove_levels(self, levels: int):
        self.level = max(0, self.level - levels)

    def total_capacity_from_worker_for_job(self, worker: Worker, job: Job):
        return get_worker_manager(worker).get_job_capacity(job) * self.workforce[job][worker]

    def get_total_job_capacity_supply(self, job: Job) -> float:
        capacity = 0
        if job in self.job_capacity_demand_per_level:
            job_workers = self.workforce[job]
            for worker_type in job_workers:
                capacity += get_worker_manager(worker_type).get_job_capacity(job) * job_workers[worker_type]
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
        if self.uses_labour:
            job_fulfillment = self.job_fulfillment
            best_fulfillment = max(job_fulfillment.values())
            shortage_fulfillment_threshold = best_fulfillment - shortage_diff
            return [job for job in job_fulfillment if job_fulfillment[job]<shortage_fulfillment_threshold]
        else:
            return []



    @property
    def job_labour_fulfillment(self) -> float:
        return min(self.job_fulfillment.values())

    @property
    def input_goods_demand(self) -> dict[Good, float]:
        return multiply_dict_by_value(self.good_consumption_per_level, self.job_labour_fulfillment * self.level)

    @property
    def output_goods_supply(self) -> dict[Good, float]:
        return multiply_dict_by_value(self.good_production_per_level, self.job_labour_fulfillment * self.level)

    @property
    def overall_market_impact(self) -> Dict[Good, float]:
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
        return goods_difference


    @property
    def max_productivity_market_impact(self) -> Dict[Good, float]:
        return multiply_dict_by_value(diff_dicts(self.good_production_per_level, self.good_consumption_per_level), self.level)

    def max_productivity_estimate_of_capacity_increase(self, worker: Worker, job: Job) -> Dict[Good, float]:
        capacity_increase = min(get_worker_manager(worker).get_job_capacity(job), self.potential_capacity_remaining(job))
        job_fulfillment_increase = capacity_increase / (self.job_capacity_demand_per_level[job] * self.level)
        return multiply_dict_by_value(self.max_productivity_market_impact, job_fulfillment_increase)

    def potential_capacity_remaining(self, job: Job) -> float:
        return self.job_capacity_demand_per_level[job]*self.level-self.get_total_job_capacity_supply(job)

    def has_capacity_for_worker_job(self, worker: Worker, job: Job) -> bool:
        worker_capacity = get_worker_manager(worker).get_job_capacity(job)
        if job in self.job_capacity_demand_per_level:
            return self.potential_capacity_remaining(job) >= worker_capacity
        else:
            return False

    def jobs_with_capacity_for_worker(self, worker: Worker) -> List[Job]:
        jobs_with_capacity = []
        for job in self.job_capacity_demand_per_level:
            if self.has_capacity_for_worker_job(worker, job):
                jobs_with_capacity.append(job)
        return jobs_with_capacity

    def add_workers(self, worker: Worker, job: Job, num: int):
        # total_added_capacity = num * get_worker_manager(worker).get_capacity(job)
        # if total_added_capacity > self.potential_capacity_remaining(job):
        if self.potential_capacity_remaining(job) <= 0:
            # raise ValueError(f"Tried to add {total_added_capacity} of {job} capacity but the maximum remaining is {self.potential_capacity_remaining(job)}")
            raise ValueError(f"Tried adding a worker for job {job} even though it's at full capacity ({self.potential_capacity_remaining(job)} remaining out of {self.job_capacity_demand_per_level[job]*self.level} total demanded)")
        else:
            self.workforce[job][worker] += num

    def max_capacity_remaining_for_worker_job(self, worker: Worker, job: Job) -> int:
        return int(self.potential_capacity_remaining(job) / get_worker_manager(worker).get_job_capacity(job))

    def remove_workers(self, worker: Worker, job: Job, num: int):
        if num>self.workforce[job][worker]:
            raise ValueError(f"Cannot remove {num} of {worker} from {job} (more than current assigned {self.workforce[job][worker]})")
        self.workforce[job][worker] = max(0, self.workforce[job][worker] - num)


