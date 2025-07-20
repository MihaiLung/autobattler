from battle_logic.character_settings.minion_base_class import MinionStats
import os

# sword_image = pygame.image.load('assets/sword.png').convert_alpha()
# sword_image = pygame.transform.scale(sword_image, (100*SCALE,100*SCALE))
#
# axe_image = pygame.image.load('assets/axe.png').convert_alpha()
# axe_image = pygame.transform.scale(axe_image, (100*SCALE,100*SCALE))

current_dir = os.path.dirname(__file__)
get_image_path = lambda im_name: os.path.join(current_dir, '..', 'assets', im_name)


elf_stats = MinionStats(
    size=100,
    health=30,
    armour=2,
    attack=8,
    attack_speed=5,
    splash_limit=1,
    movement_speed=2,
    mass=100,
    image_loc="assets/elf.png",
    attack_cooldown=30
    # weapon=sword_image,
)

orc_stats = MinionStats(
    size=120,
    health=50,
    armour=1,
    attack=50,
    attack_speed=2,
    splash_limit=1,
    movement_speed=1,
    mass=200,
    image_loc="assets/orc.png",
    attack_cooldown=120
    # weapon=pygame.transform.scale(axe_image,(200*SCALE,200*SCALE)),
)