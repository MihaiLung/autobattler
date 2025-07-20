import pygame
import random
import math

# Colors (for the dummy player sprite)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


class DeathAnimation(pygame.sprite.Sprite):
    """
    A Pygame sprite class that creates a "death animation" by shattering
    an original sprite into multiple masked slices that fly away and fade out.
    """

    def __init__(self, original_sprite, num_slices_x=5, num_slices_y=5):
        """
        Initializes the DeathAnimation object.

        Args:
            original_sprite (pygame.sprite.Sprite): The sprite to be "shattered".
                                                    Its image and rect are used.
            num_slices_x (int): The number of horizontal slices to divide the sprite into.
            num_slices_y (int): The number of vertical slices to divide the sprite into.
        """
        super().__init__()
        # Ensure the original image has an alpha channel for proper transparency handling
        self.original_image = original_sprite.image_raw.convert_alpha()
        self.original_rect = original_sprite.rect

        self.slices = []  # List to hold individual slice sprites
        self.slice_group = pygame.sprite.Group()  # Pygame group for easier drawing/updating

        # Calculate dimensions for each slice
        self.slice_width = self.original_image.get_width() // num_slices_x
        self.slice_height = self.original_image.get_height() // num_slices_y

        # Calculate the center of the original sprite for the "shatter" effect direction
        center_x = self.original_rect.centerx
        center_y = self.original_rect.centery

        # Iterate through the grid to create each slice
        for y in range(num_slices_y):
            for x in range(num_slices_x):
                # Define the rectangle for the current slice within the original image
                slice_rect_in_original = pygame.Rect(
                    x * self.slice_width, y * self.slice_height,
                    self.slice_width, self.slice_height
                )
                # Create a new surface for the slice, ensuring it has an alpha channel
                slice_image = pygame.Surface(
                    (self.slice_width, self.slice_height), pygame.SRCALPHA
                )
                # Blit the relevant part of the original image onto the new slice surface
                slice_image.blit(self.original_image, (0, 0), slice_rect_in_original)

                # Apply a random mask to the slice image
                # masked_image = self._apply_mask(slice_image)
                masked_image = slice_image.copy()

                # Create a new Pygame sprite for this individual slice
                slice_sprite = pygame.sprite.Sprite()
                slice_sprite.image = masked_image
                # Position the slice sprite relative to the original sprite's top-left corner
                slice_sprite.rect = masked_image.get_rect(
                    topleft=(self.original_rect.left + x * self.slice_width,
                             self.original_rect.top + y * self.slice_height)
                )

                # Calculate initial velocity for the "shatter" effect
                # This vector points from the original sprite's center to the slice's center
                slice_center_x = slice_sprite.rect.centerx
                slice_center_y = slice_sprite.rect.centery

                dx = slice_center_x - center_x
                dy = slice_center_y - center_y

                # Normalize the vector and scale by a random speed
                magnitude = math.sqrt(dx ** 2 + dy ** 2)
                if magnitude == 0:
                    # Handle the rare case of a slice being exactly at the center
                    # Give it a small, random initial push
                    velocity_x = random.uniform(-1, 1) * 3
                    velocity_y = random.uniform(-1, 1) * 3
                else:
                    # Base speed for the shatter, with some randomness
                    base_speed = random.uniform(3, 7)*0.2
                    velocity_x = (dx / magnitude) * base_speed + random.uniform(-1, 1)
                    velocity_y = (dy / magnitude) * base_speed + random.uniform(-1, 1)

                slice_sprite.velocity = pygame.math.Vector2(velocity_x, velocity_y)
                slice_sprite.alpha = 255  # Initial alpha (fully opaque) for fading effect

                self.slices.append(slice_sprite)
                self.slice_group.add(slice_sprite)


    def update(self):
        """
        Updates the position and alpha (fading) of each individual slice.
        Removes slices that are fully faded or off-screen.
        """
        # Iterate over a copy of the list to safely remove elements during iteration
        for slice_sprite in list(self.slices):
            # Update position based on velocity
            slice_sprite.rect.x += slice_sprite.velocity.x
            slice_sprite.rect.y += slice_sprite.velocity.y

            # Gradually decrease alpha for fading effect
            slice_sprite.alpha -= 5  # Adjust this value to change fade speed
            if slice_sprite.alpha < 0:
                slice_sprite.alpha = 0  # Ensure alpha doesn't go below 0

            # Apply the new alpha to the slice's image
            slice_sprite.image.set_alpha(slice_sprite.alpha)

            # Remove the slice if it's fully transparent or has moved off-screen
            if slice_sprite.alpha == 0:
                self.slices.remove(slice_sprite)
                self.slice_group.remove(slice_sprite)

    def draw(self, screen_surface):
        """
        Draws all active slices of the death animation to the given screen surface.

        Args:
            screen_surface (pygame.Surface): The surface to draw the slices onto.
        """
        self.slice_group.draw(screen_surface)

