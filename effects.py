import pygame
from minions.minion_stats import elf_stats
from settings import SCALE


class WeaponSwing(pygame.sprite.Sprite):
    """
    A Pygame sprite class to represent a weapon swinging in an arc.

    The weapon image is blitted onto a larger transparent surface (megasurface)
    which is then rotated around a specified origin point. This allows for easy
    rotation of the weapon while ensuring it stays outside the origin rect.

    Args:
        origin_point (tuple): (x, y) coordinates of the center of rotation for the swing.
                              This is typically the center of the player/entity.
        origin_rect (pygame.Rect): A square rect representing the player/entity.
                                   The weapon will be positioned just outside this rect.
        direction_of_swing (float): The central angle (in degrees) of the 90-degree swing arc.
                                    0 degrees is right, 90 is down, 180 is left, 270 is up.
        weapon_image_surface (pygame.Surface): The image of the weapon. It is assumed
                                               to be pointing upwards (0 degrees) in its
                                               original state.
        swing_speed (float, optional): The speed of the swing in degrees per frame.
                                       Defaults to 10.0.
    """
    def __init__(self, origin_point: pygame.Vector2, origin_rect: pygame.Rect, direction_of_swing: pygame.Vector2, weapon_image_surface, swing_speed=3.0):
        super().__init__()

        self.origin_point = origin_point
        self.origin_rect = origin_rect
        self.original_weapon_image = weapon_image_surface.convert_alpha()
        self.weapon_rect = self.original_weapon_image.get_rect()

        self.total_swing_angle = 90.0
        self.swing_speed = swing_speed

        # Calculate the distance from the origin_point to the weapon's pivot.
        # This ensures the weapon starts just outside the origin_rect.
        # Adding a small padding for visual separation.
        self.swing_radius = self.origin_rect.width / 2 + 10

        # Define the start and end angles of the 90-degree arc.
        # The direction_of_swing is the center of this arc.
        swing_angle = direction_of_swing.angle_to(pygame.Vector2(0, 1))

        self.start_angle = swing_angle - (self.total_swing_angle / 2)
        self.current_angle = self.start_angle
        self.end_angle = self.start_angle + self.total_swing_angle

        # --- Create the "megasurface" ---
        # This surface will contain the weapon image at a fixed offset,
        # and this entire surface will be rotated.
        # Calculate max dimension needed for the megasurface to contain the weapon
        # at any rotation around its pivot point relative to the megasurface center.
        # It needs to be large enough to contain the weapon when it's at its furthest
        # point from the megasurface's center (i.e., swing_radius + weapon_height).
        # We multiply by 2 for diameter and add some extra padding.
        max_dim = int(2 * (self.swing_radius + self.weapon_rect.height) + 50) # Added extra padding for safety
        self.base_megasurface = pygame.Surface((max_dim, max_dim), pygame.SRCALPHA)
        self.base_megasurface_center = pygame.math.Vector2(max_dim / 2, max_dim / 2)

        # Blit the original weapon image onto the base_megasurface.
        # The weapon's pivot (its bottom-center) should be positioned 'swing_radius'
        # units directly "above" the megasurface's center.
        # (Assuming original weapon image points up, so its base is at its bottom-center).
        weapon_pivot_on_megasurface = self.base_megasurface_center - pygame.math.Vector2(0, self.swing_radius)
        # Calculate top-left position for blitting the weapon image
        weapon_topleft_on_megasurface = weapon_pivot_on_megasurface - pygame.math.Vector2(
            self.weapon_rect.width / 2, self.weapon_rect.height
        )
        self.base_megasurface.blit(self.original_weapon_image, weapon_topleft_on_megasurface)

        # Initialize the current image and rect for the sprite
        self.image = self.base_megasurface.copy()
        self.rect = self.image.get_rect(center=self.origin_point)

    def update(self):
        """
        Updates the swing animation. Rotates the weapon and kills the sprite
        once the swing arc is completed.
        """
        self.current_angle += self.swing_speed

        # Check if the swing has completed its 90-degree arc
        if self.current_angle > self.end_angle:
            self.kill() # Remove the sprite from all groups
            return

        # Calculate the rotation angle for Pygame's transform.rotate.
        # The original weapon image points up (0 degrees).
        # If current_angle is 0 (right), we need to rotate it -90 degrees.
        # If current_angle is 90 (down), we need to rotate it -180 degrees.
        # So, the angle to rotate the base_megasurface is (current_angle - 90).
        # Pygame's rotate function rotates counter-clockwise, so we negate the angle.
        rotation_for_pygame = self.current_angle - 90
        self.image = pygame.transform.rotate(self.base_megasurface, -rotation_for_pygame)

        # Update the rect to keep the center of the rotated megasurface
        # aligned with the origin_point.
        self.rect = self.image.get_rect(center=self.origin_point)
