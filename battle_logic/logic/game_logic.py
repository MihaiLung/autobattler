from battle_logic.animations.destroy_animation import DeathAnimation
from battle_logic.character import DamageAction, CharacterGroup, Character  # , AttackImpactSprite
from battle_logic.logic.utils import get_all_quadrants, get_colliding_sprites, sprite_distance, is_sprite_on_edge
from settings import *




def get_attack_visuals(all_group):
    attack_animations = pygame.sprite.Group()
    for sprite in all_group:
        if sprite.active_animator is not None:
            attack_animations.add(sprite.active_animator.attack_sprite)
    return attack_animations


def update_group_states(friends: CharacterGroup, enemies: CharacterGroup, attack_animations):
    need_refresh_targets = False
    for char in friends:
        game_action = char.update()
        if type(game_action) == DeathAnimation:
            attack_animations.add(game_action)
            need_refresh_targets = True
            if "elf" in char.stats.image_loc:
                nearby_allies = pygame.sprite.spritecollide(char, friends, False)
                for ally in nearby_allies:
                    ally.speed *= 1.1
                    ally.attack_speed *= 1.1
                    ally.recompute_attack_timer()
    if need_refresh_targets:
        if min(len(friends), len(enemies)) == 0:
            pygame.event.post(pygame.event.Event(GameEvents.BattleDone.value))
        else:
            enemies.set_targets(friends)
            friends.set_targets(enemies)


def get_sprite_move_extent(s, ref):
    move_extent = s.willingness_to_move
    return move_extent * 4 if is_sprite_on_edge(ref) else move_extent


def resolve_collisions(allies_group, enemy_group):

    collision_group = pygame.sprite.Group()
    collision_group.add(allies_group.sprites())
    collision_group.add(enemy_group.sprites())

    collision_groups = []
    quadrants = get_all_quadrants()
    for quadrant in quadrants:
        collision_groups.append(get_colliding_sprites(quadrant, collision_group))
    for collision_group in collision_groups:
        collision_group.sort(key=lambda x: x.collision_resolution_priority)
        for i, sprite in enumerate(collision_group[:-1]):
            for reference in collision_group[i+1:]:
                linking_vector = sprite.central_position_for_collision - reference.central_position_for_collision
                overlap = -sprite_distance(reference, sprite)
                # Apply strong force if overlap considerable


                if overlap > 0:
                    separation_vector = linking_vector.clamp_magnitude(overlap)*0.5
                    # If enemies, fully repulse everytime
                    if (sprite in allies_group) and (reference not in allies_group):
                        sprite.next_move += separation_vector/2*get_sprite_move_extent(sprite, reference)
                        reference.next_move -= separation_vector/2*get_sprite_move_extent(reference, sprite)
                    else:
                        reference.next_move -= separation_vector*get_sprite_move_extent(reference, sprite)
                # If getting close to overlapping but not quite there yet, start applying teeny push
                elif overlap > -(sprite.diameter + reference.diameter)/10:
                    if (sprite in allies_group) and (reference in allies_group):
                        separation_vector = linking_vector*0.0005
                        reference.next_move -= separation_vector*get_sprite_move_extent(reference, sprite)

