from dataclasses import dataclass

@dataclass
class MinionStats:
    size: int
    health: int
    armour: int
    attack: int
    attack_speed: float
    movement_speed: float
    mass: int
    image_loc: str