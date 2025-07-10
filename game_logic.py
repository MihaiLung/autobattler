import pygame

from character import DamageAction
from utils import get_all_quadrants, get_colliding_sprites, sprite_distance, is_sprite_on_edge


def get_attack_visuals(all_group):
    attack_animations = pygame.sprite.Group()
    for sprite in all_group:
        if sprite.active_animator is not None:
            attack_animations.add(sprite.active_animator.attack_sprite)
    return attack_animations


def update_all_character_states(orc_group, elf_group):    # Update character states
    need_refresh_targets = False
    for char in orc_group:
        game_action = char.update()
        if type(game_action) == DamageAction:
            # Resolve damage
            char.deal_damage(char.target)
            char.target.update_image()

        elif game_action == "dead":
            need_refresh_targets = True
    if need_refresh_targets:
        elf_group.set_targets(orc_group)

    need_refresh_targets = False
    for char in elf_group:
        game_action = char.update()
        if type(game_action) == DamageAction:
            # Resolve damage
            char.deal_damage(char.target)
            char.target.update_image()

        elif game_action == "dead":
            need_refresh_targets = True
    if need_refresh_targets:
        orc_group.set_targets(elf_group)


def resolve_collisions(group):
    collision_groups = []
    quadrants = get_all_quadrants()
    for quadrant in quadrants:
        collision_groups.append(get_colliding_sprites(quadrant, group))
    for collision_group in collision_groups:
        for i, sprite in enumerate(collision_group[:-1]):
            for reference in collision_group[i+1:]:
                linking_vector = sprite.position - reference.position
                overlap = -sprite_distance(reference, sprite)
                if overlap > 0:
                    mass_ratio = sprite.stats.mass / reference.stats.mass
                    separation_vector = linking_vector.clamp_magnitude(overlap)
                    if sprite.collision_enabled:
                        sprite.next_move += separation_vector/mass_ratio
                    if reference.collision_enabled:
                        reference.next_move -= separation_vector*mass_ratio

                    # If one or both of the sprites are stuck on the corner, significantly increase the force to declump corners
                    if is_sprite_on_edge(sprite):
                        if reference.collision_enabled:
                            reference.next_move -= 4*separation_vector
                        if sprite.collision_enabled:
                            sprite.next_move += 4*separation_vector
                    if is_sprite_on_edge(reference):
                        if reference.collision_enabled:
                            reference.next_move -= 4*separation_vector
                        if sprite.collision_enabled:
                            sprite.next_move += 4*separation_vector



                    #
                    # # Sprite update
                    # for s in (sprite, reference):
                    #     if s.next_move.magnitude()>0:
                    #         if s is sprite:
                    #             projection_on_sprite = linking_vector.project(s.next_move)
                    #         else:
                    #             projection_on_sprite = -linking_vector.project(s.next_move)
                    #         cm = s.next_move.magnitude()
                    #         s.next_move = s.next_move+projection_on_sprite
                    #         s.next_move = s.next_move.clamp_magnitude(min(cm, s.next_move.magnitude()))




                    # weight_diff = sprite.stats.mass**2/reference.stats.mass**2
                    # decollision_vector = linking_vector.clamp_magnitude(overlap/2)
                    # sprite.next_move += decollision_vector/weight_diff
                    # reference.next_move -= decollision_vector*weight_diff

                    # If significant overlap, move away from each other
                    # if clip.height*clip.width>(reference.rect.height**2+sprite.rect.height**2)/10:
                    #     linking_vector = sprite.position - reference.position
                    #     sprite.next_move = linking_vector.normalize()*sprite.speed
                    #     reference.next_move = -linking_vector.normalize()*reference.speed
                    # # If small overlap, simply average vector
                    # else:
                    #     common_vector = (reference.next_move + sprite.next_move)/2
                    #     reference.next_move = common_vector
                    #     sprite.next_move = common_vector


