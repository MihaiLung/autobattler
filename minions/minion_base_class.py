from dataclasses import dataclass

import pygame


@dataclass
class MinionStats:
    size: int
    health: int
    armour: int
    attack: int
    attack_speed: float
    splash_limit: int
    movement_speed: float
    mass: int
    image_loc: str
    weapon: pygame.Surface
    attack_cooldown: int = 90