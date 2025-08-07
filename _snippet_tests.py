import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Death Animation")

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
        self.original_image = original_sprite.image.convert_alpha()
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

    def _apply_mask(self, surface):
        """
        Applies a random irregular polygon or triangle mask to the given surface.

        Args:
            surface (pygame.Surface): The original slice surface to be masked.

        Returns:
            pygame.Surface: A new surface with the mask applied,
                            making parts outside the mask transparent.
        """
        mask_type = random.choice(['triangle', 'polygon'])  # Choose a random mask shape

        width, height = surface.get_size()
        # Create a new surface for the masked result. It must have an alpha channel.
        masked_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create a temporary mask surface. This surface will define the shape.
        temp_mask = pygame.Surface((width, height), pygame.SRCALPHA)
        # Draw the desired shape in a solid, opaque color (e.g., white with full alpha)
        # on the temp_mask. This white area will be the visible part of the slice.

        points = []
        if mask_type == 'triangle':
            # Generate 3 random points within the slice's bounds
            points = [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ]
        elif mask_type == 'polygon':
            # Generate 4 to 6 random points for an irregular polygon
            num_points = random.randint(4, 6)
            for _ in range(num_points):
                points.append((random.randint(0, width), random.randint(0, height)))

        # Draw the polygon on the temporary mask surface.
        # The color (255, 255, 255, 255) means opaque white.
        pygame.draw.polygon(temp_mask, (255, 255, 255, 255), points)

        # Blit the original slice image onto the masked_surface.
        masked_surface.blit(surface, (0, 0))

        # Now, blit the temp_mask onto the masked_surface using BLEND_RGBA_MULT.
        # This special flag multiplies the alpha channels of the source (temp_mask)
        # and the destination (masked_surface).
        # - Where temp_mask is transparent (alpha 0), masked_surface's alpha becomes 0.
        # - Where temp_mask is opaque (alpha 255), masked_surface's alpha remains unchanged.
        # This effectively cuts out the shape defined by temp_mask.
        masked_surface.blit(temp_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return masked_surface

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
            if slice_sprite.alpha == 0 or not screen.get_rect().colliderect(slice_sprite.rect):
                self.slices.remove(slice_sprite)
                self.slice_group.remove(slice_sprite)

    def draw(self, screen_surface):
        """
        Draws all active slices of the death animation to the given screen surface.

        Args:
            screen_surface (pygame.Surface): The surface to draw the slices onto.
        """
        self.slice_group.draw(screen_surface)


# --- Dummy Sprite for Demonstration ---
class Player(pygame.sprite.Sprite):
    """
    A simple player sprite used to demonstrate the death animation.
    It's a blue square with a red circle.
    """

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50], pygame.SRCALPHA)  # Create a surface with alpha
        self.image.fill(BLUE)  # Fill with blue
        pygame.draw.circle(self.image, RED, (25, 25), 20)  # Draw a red circle inside
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))


# --- Main Game Loop ---
def main():
    """
    The main function that sets up the game, runs the loop, and demonstrates
    the DeathAnimation class.
    """
    player = Player()  # Create an initial player sprite
    all_sprites = pygame.sprite.Group(player)  # Group to manage the player sprite
    death_animations = []  # List to hold active death animation instances

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # If the player is alive, trigger the death animation
                    if player.alive():
                        # Create a new DeathAnimation instance
                        # You can change num_slices_x and num_slices_y here
                        new_death_anim = DeathAnimation(player, num_slices_x=8, num_slices_y=8)
                        death_animations.append(new_death_anim)
                        player.kill()  # Remove the original player sprite from its group
                if event.key == pygame.K_r:  # Press 'R' to reset the player
                    if not player.alive():  # Only reset if the player is currently "dead"
                        player = Player()
                        all_sprites.add(player)  # Add the new player back to the sprite group
                        death_animations.clear()  # Clear any lingering death animations

        # Update all active sprites and death animations
        all_sprites.update()
        for anim in list(death_animations):  # Iterate over a copy to allow removal
            anim.update()
            if not anim.slices:  # If an animation has no more active slices, remove it
                death_animations.remove(anim)

        # Drawing
        screen.fill(BLACK)  # Clear the screen with black background

        all_sprites.draw(screen)  # Draw the player sprite (if it's still alive)

        # Draw all active death animation slices
        for anim in death_animations:
            anim.draw(screen)

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pygame.quit()  # Uninitialize Pygame modules


if __name__ == "__main__":
    main()
