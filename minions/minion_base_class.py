from dataclasses import dataclass

@dataclass
class MinionStats:
    health: int
    armour: int
    attack: int
    attack_speed: float
    movement_speed: float
    mass: int
    image_loc: str
    is_player_controlled: bool