from battle_logic.character_settings.minion_base_class import MinionStats
import os
from battle_logic.abilities.berserk import Berserker


elf_stats = MinionStats(
    size=100,
    health=30,
    armour=0,
    attack=8,
    attack_speed=3,
    splash_limit=1,
    movement_speed=2,
    mass=100,
    image_loc="elf.png",
    attack_cooldown=30
)

orc_stats = MinionStats(
    size=120,
    health=50,
    armour=2,
    attack=35,
    attack_speed=2,
    splash_limit=5,
    movement_speed=1,
    mass=200,
    image_loc="orc.png",
    attack_cooldown=120,
    abilities=[Berserker]
)