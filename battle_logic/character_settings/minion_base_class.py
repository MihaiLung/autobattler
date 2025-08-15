from dataclasses import dataclass
from typing import Optional, List, Tuple

import pygame

from economy.worker import Worker


@dataclass
class MinionStats:
    name: str
    size: int
    health: int
    armour: int
    attack: int
    attack_speed: float
    splash_limit: int
    movement_speed: float
    mass: int
    image_loc: str
    race: Worker
    attack_cooldown: int = 90
    abilities: Optional[List] = None