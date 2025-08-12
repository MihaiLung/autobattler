from typing import List, Dict
from dataclasses import dataclass, fields
import enum
from goods import Good


def get_worker_manager(worker):
    return WORKER_MANAGERS[worker.value]


class Job(enum.Enum):
    FARMING = 1
    WOODCUTTING = 2
    MAGIC = 3

job_names = {
    Job.FARMING: "Farming",
    Job.WOODCUTTING: "Woodcutting",
    Job.MAGIC: "Magic"
}


@dataclass
class JobCapacity:
    job: Job
    value: float

    def __post_init__(self):
        if not isinstance(self.job, Job):
            raise TypeError("Must be a valid job")

default_suitabilities = {job: 3 if job != Job.MAGIC else 0 for job in Job}

@dataclass
class WorkerManager:
    custom_job_capacities: List[JobCapacity]
    sustenance_goods: Dict[Good, float]

    def __post_init__(self):
        # Validate input
        if not isinstance(self.custom_job_capacities, list):
            raise TypeError("Must be a valid list suitabilities")
        for capacity in self.custom_job_capacities:
            if not isinstance(capacity, JobCapacity):
                raise TypeError("Must be a valid JobSuitability")

    def get_capacity(self, job: Job):
        for proficiency in self.custom_job_capacities:
            if proficiency.job == job:
                return proficiency.value
        else:
            return 0



class Worker(enum.Enum):
    """
    Ensure the strings are unique.
    """
    ELF = 'elf'
    ORC = 'orc'

WORKER_MANAGERS = {
    Worker.ELF.value:  WorkerManager(
        [
            JobCapacity(Job.FARMING, 5),
            JobCapacity(Job.WOODCUTTING, 2),
            JobCapacity(Job.MAGIC, 3),
        ],
        {
            Good.GRAIN: 1
        }
    ),
    Worker.ORC.value:  WorkerManager(
        [
            JobCapacity(Job.FARMING, 1),
            JobCapacity(Job.WOODCUTTING, 5),
            JobCapacity(Job.MAGIC, 0),
        ],
        {
            Good.MEAT: 1
        }
    )
}