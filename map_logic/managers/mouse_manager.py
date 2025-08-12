import pygame

from map_logic.info_window import InformationWindow
from utils import tadd, tdiff


class MouseManager():
    def __init__(self):
        self.active_window = None
        self.start_mouse_pos = None
        self.start_rect = None

    def register_clicked_object(self, window: InformationWindow, mouse_pos):
        self.active_window = window
        self.start_mouse_pos = mouse_pos
        self.start_rect = window.rect.copy()

    def reset_clicked_object(self):
        self.active_window = None
        self.start_mouse_pos = None

    def get_current_mouse_offset(self):
        return tdiff(pygame.mouse.get_pos(), self.start_mouse_pos)

    def update(self):
        if self.active_window:
            self.active_window.rect.topleft = tadd(self.start_rect.topleft, self.get_current_mouse_offset())