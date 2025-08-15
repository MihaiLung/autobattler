from battle_logic.character_settings.minion_base_class import MinionStats
import os
from battle_logic.abilities.berserk import Berserker
from economy.worker import Worker
from enum import Enum

class Minion(Enum):
    RANGER = 'ranger'
    BERSERKER = 'berserker'


elf_stats = MinionStats(
    name="Ranger",
    size=100,
    health=100,
    armour=0,
    attack=8,
    attack_speed=4,
    splash_limit=1,
    movement_speed=2,
    mass=100,
    image_loc="elf.png",
    attack_cooldown=30,
    race=Worker.ELF,
)

orc_stats = MinionStats(
    name="Berserker",
    size=120,
    health=180,
    armour=2,
    attack=35,
    attack_speed=2,
    splash_limit=5,
    movement_speed=1,
    mass=200,
    image_loc="orc.png",
    attack_cooldown=120,
    race=Worker.ORC,
    abilities=[Berserker]
)

MINION_TO_STATS = {
    Minion.BERSERKER: orc_stats,
    Minion.RANGER: elf_stats,
}