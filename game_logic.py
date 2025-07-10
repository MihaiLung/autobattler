import pygame

from character import DamageAction
from utils import get_all_quadrants, get_colliding_sprites, sprite_distance


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
                    separation_vector = linking_vector.clamp_magnitude(overlap)
                    sprite.next_move += separation_vector
                    reference.next_move -= separation_vector



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


