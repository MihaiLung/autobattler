import os
import pygame
from typing import Dict

def get_asset_path(filename):
    """
    Constructs a path to an asset file relative to the script's location.

    Args:
        filename (str): The name of the asset file (e.g., 'goodboy.png').

    Returns:
        str: The absolute path to the asset file.
    """
    # Get the directory of the currently executing script.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the assets directory, which is a sibling of the script's directory.
    assets_dir = os.path.join(script_dir, 'assets')

    # Construct the full path to the file.
    file_path = os.path.join(assets_dir, filename)

    return file_path

def load_image(filename):
    return pygame.image.load(get_asset_path(filename)).convert_alpha()

def multiply_dict_by_value(d: Dict, m: float):
    return {key: d[key]*m for key in d}

def add_dicts(d1, d2):
    d = {}
    for key in set(d1.keys()) | set(d2.keys()):
        d[key] = d1.get(key, 0) + d2.get(key, 0)
    return d

def diff_dicts(d1, d2):
    d = {}
    for key in set(d1.keys()) | set(d2.keys()):
        d[key] = d1.get(key, 0) - d2.get(key, 0)
    return d


def tadd(tuple1, tuple2):
    return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]


def tdiff(tuple1, tuple2):
    return tuple1[0] - tuple2[0], tuple1[1] - tuple2[1]

def bound_rect_within_screen(rect: pygame.Rect, surface: pygame.Surface):
    if rect.left<0:
        rect.left = 0
    if rect.right>surface.get_width():
        rect.right = surface.get_width()
    if rect.top<0:
        rect.top = 0
    if rect.bottom>surface.get_height():
        rect.bottom = surface.get_height()
    return rect