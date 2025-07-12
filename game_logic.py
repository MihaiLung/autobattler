import pygame

from character import DamageAction, AttackImpactSprite
from effects import WeaponSwing
from utils import get_all_quadrants, get_colliding_sprites, sprite_distance, is_sprite_on_edge


def get_attack_visuals(all_group):
    attack_animations = pygame.sprite.Group()
    for sprite in all_group:
        if sprite.active_animator is not None:
            attack_animations.add(sprite.active_animator.attack_sprite)
    return attack_animations


def update_group_states(friends, enemies, attack_animations):
    need_refresh_targets = False
    for char in friends:
        game_action = char.update()
        if type(game_action) == DamageAction:
            # Resolve damage
            char.deal_damage(char.target)
            char.target.update_image()
        elif type(game_action) == AttackImpactSprite:
            attack_animations.add(game_action)
        elif game_action == "dead":
            need_refresh_targets = True
    if need_refresh_targets:
        enemies.set_targets(friends)


def resolve_collisions(group):
    collision_groups = []
    quadrants = get_all_quadrants()
    for quadrant in quadrants:
        collision_groups.append(get_colliding_sprites(quadrant, group))
    for collision_group in collision_groups:
        for i, sprite in enumerate(collision_group[:-1]):
            for reference in collision_group[i+1:]:
                linking_vector = sprite.central_position - reference.central_position
                overlap = -sprite_distance(reference, sprite)
                if overlap > 0.05:
                    mass_ratio = sprite.stats.mass / reference.stats.mass
                    mass_ratio = 1
                    if linking_vector.magnitude()>0:
                        # sprite_relative_willingness_to_move = 1
                        # if sprite.collision_enabled:
                        #     sprite_relative_willingness_to_move *=
                        # if reference.collision_enabled:
                        #     sprite_relative_willingness_to_move /= 1
                        # separation_vector = linking_vector.clamp_magnitude(overlap)
                        # sprite.next_move += separation_vector/mass_ratio*min(1/sprite_relative_willingness_to_move, 1)
                        # reference.next_move -= separation_vector*mass_ratio*min(sprite_relative_willingness_to_move, 1)

                        def get_sprite_move_extent(s, ref):
                            move_extent = s.willingness_to_move
                            return move_extent*4 if is_sprite_on_edge(ref) else move_extent

                        # sprite_move_extent = 1 if sprite.collision_enabled else 0.001
                        # reference_move_extent = 1 if reference.collision_enabled else 0.001
                        separation_vector = linking_vector.clamp_magnitude(overlap)
                        sprite.next_move += separation_vector/mass_ratio*get_sprite_move_extent(sprite, reference)
                        reference.next_move -= separation_vector*mass_ratio*get_sprite_move_extent(reference, sprite)

                        # # If one or both of the sprites are stuck on the corner, significantly increase the force to declump corners
                        # if is_sprite_on_edge(sprite):
                        #     if reference.collision_enabled:
                        #         reference.next_move -= 4*separation_vector
                        #     if sprite.collision_enabled:
                        #         sprite.next_move += 4*separation_vector
                        # if is_sprite_on_edge(reference):
                        #     if reference.collision_enabled:
                        #         reference.next_move -= 4*separation_vector
                        #     if sprite.collision_enabled:
                        #         sprite.next_move += 4*separation_vector


                        #
                        # separation_vector = linking_vector.clamp_magnitude(overlap)
                        # if sprite.collision_enabled:
                        #     sprite.next_move += separation_vector/mass_ratio
                        # if reference.collision_enabled:
                        #     reference.next_move -= separation_vector*mass_ratio
                        #
                        # # If one or both of the sprites are stuck on the corner, significantly increase the force to declump corners
                        # if is_sprite_on_edge(sprite):
                        #     if reference.collision_enabled:
                        #         reference.next_move -= 4*separation_vector
                        #     if sprite.collision_enabled:
                        #         sprite.next_move += 4*separation_vector
                        # if is_sprite_on_edge(reference):
                        #     if reference.collision_enabled:
                        #         reference.next_move -= 4*separation_vector
                        #     if sprite.collision_enabled:
                        #         sprite.next_move += 4*separation_vector
                        #
