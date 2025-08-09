import pygame

from settings import ENEMIES_CONFIG_DTYPE, WIDTH, HEIGHT
from utils import get_asset_path
from typing import Optional


def crop_to_square(image: pygame.Surface) -> pygame.Surface:
    """
    Crops a pygame.Surface to a square, centering the crop.

    Args:
        image: The pygame.Surface to crop.

    Returns:
        A new pygame.Surface that is a square version of the original.
    """
    width, height = image.get_size()

    # Determine the smaller dimension, which will be the side of the new square.
    side = min(width, height)

    # Calculate the starting coordinates for the crop.
    if width > height:
        # The image is wider than it is tall, so crop from the left and right sides.
        x_start = (width - side) // 2
        y_start = 0
    else:
        # The image is taller than it is wide, so crop from the top and bottom.
        x_start = 0
        y_start = (height - side) // 2

    # Create the source rectangle for the crop.
    source_rect = pygame.Rect(x_start, y_start, side, side)

    # Create a new surface for the square image.
    square_image = pygame.Surface((side, side), pygame.SRCALPHA)

    # Blit the cropped portion of the original image onto the new square surface.
    square_image.blit(image, (0, 0), source_rect)

    return square_image.convert_alpha()

def load_square_image(loc):
    return crop_to_square(pygame.image.load(get_asset_path(loc)).convert_alpha())

class CircularImageSprite(pygame.sprite.Sprite):
    def __init__(self, image_location, center, enemies_config: Optional[ENEMIES_CONFIG_DTYPE] = None, radius=60, border_color="green", border_width=8):
        """
        Initializes a circular sprite with a bordered image.

        Args:
            image_location (str): The file path to the image.
            center (tuple): The (x, y) coordinates for the center of the sprite.
            radius (int): The radius of the outer circle (including the border).
            border_color (tuple): The RGB color of the border.
            border_width (int): The width of the border in pixels.
        """
        super().__init__()

        center = center[0]*WIDTH, center[1]*HEIGHT

        # --- Load and Scale Image ---
        self.encounter_image = load_square_image(image_location)
        self.cleared_image = load_square_image("farm_icon.png")
        self.enemies_config = enemies_config


        self.radius = radius
        self.border_width = border_width
        self.center = center
        self.border_color = border_color

        # Calculate the inner radius for the image
        self.inner_radius = self.radius - self.border_width
        self.image_size = (self.inner_radius * 2, self.inner_radius * 2)
        # self.scaled_image = pygame.transform.smoothscale(self.encounter_image, self.image_size)

        self.is_highlighted = False
        self.is_cleared = False
        self.refresh_image(self.is_highlighted)

    def refresh_image(self, border: bool = False):
        # --- Create a circular image with alpha channel ---
        # Create a surface for the inner image circle
        self.image = pygame.Surface(self.image_size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (self.inner_radius, self.inner_radius), self.inner_radius)


        icon = self.cleared_image if self.is_cleared else self.encounter_image
        scaled_icon = pygame.transform.scale(icon, self.image_size)
        self.image.blit(scaled_icon, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # --- Combine with Border ---
        # Create a new surface large enough for the border
        final_image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # Draw the outer border circle
        if border:
            pygame.draw.circle(final_image, self.border_color, (self.radius, self.radius), self.radius)
        # Blit the inner circular image onto the final surface
        final_image.blit(self.image, (self.border_width, self.border_width))

        self.image = final_image
        self.rect = self.image.get_rect(center=self.center)



    def update(self):
        # Add any update logic here if needed, for example, movement.
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)