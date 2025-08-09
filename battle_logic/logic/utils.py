import pygame

from settings import *
from typing import List
import random

def vector_to_integer_tuple(vector: pygame.Vector2) -> tuple[int, int]:
    return int(vector.x), int(vector.y)

def get_closest_target(s, target_group):
    if len(target_group) == 0:
        return None
    else:
        return min(target_group, key=lambda t: (s.rect.centerx - t.rect.centerx) ** 2 + (s.rect.centery - t.rect.centery) ** 2)


def yield_array_elements(arr):
    """
    Yields elements of a NumPy array one by one.
    After yielding all elements, subsequent calls to next() will raise StopIteration.
    """
    for item in arr.flat: # .flat flattens any array into an iterator
        yield item

def get_random_point_in_rect(rect):
    """
    Returns a random (x, y) coordinate pair within the given pygame.Rect.

    Args:
        rect (pygame.Rect): The rectangle to get a random point from.

    Returns:
        tuple: A tuple (x, y) representing a random point within the rect.
    """
    random_x = random.randint(rect.left, rect.right - 1)
    random_y = random.randint(rect.top, rect.bottom - 1)
    return (random_x, random_y)

def is_sprite_on_edge(char: pygame.sprite.Sprite) -> bool:
    if char.rect.left==0 or char.rect.top==0:
        return True
    elif char.rect.right==WIDTH:
        return True
    elif char.rect.bottom==HEIGHT:
        return True
    else:
        return False

def sprite_distance(sprite1, sprite2):
    """
    Gets distance between two sprites, reduced by their respective radii. Assumes spherical-ish sprites.
    :param sprite1:
    :param sprite2:
    :return:
    """
    radii = (sprite1.diameter + sprite2.diameter) / 2
    linking_vector = (sprite1.central_position_for_collision - sprite2.central_position_for_collision)
    return linking_vector.magnitude()-radii

def get_colliding_sprites(target_rect: pygame.Rect, sprite_group: pygame.sprite.Group):
    """
    Returns all sprites in a given sprite group that collide with a target rect.

    Args:
        target_rect (pygame.Rect): The rect to check for collisions against.
        sprite_group (pygame.sprite.Group): The group of sprites to check for collisions within.

    Returns:
        list: A list of sprites from the group that are colliding with the target_rect.
    """
    colliding_sprites = []
    for sprite in sprite_group:
        # if sprite.collision_enabled:
            if target_rect.colliderect(sprite.rect):
                colliding_sprites.append(sprite)
    return colliding_sprites

def get_all_quadrants(width=WIDTH, height=HEIGHT) -> List[pygame.Rect]:

    quadrants = []

    left = 0
    while left<width:
        top = 0
        while top<height:
            quadrants.append(pygame.Rect(left, top, COLLISION_QUADRANT_SIZE, COLLISION_QUADRANT_SIZE))
            top += COLLISION_QUADRANT_SIZE
        left += COLLISION_QUADRANT_SIZE

    return quadrants