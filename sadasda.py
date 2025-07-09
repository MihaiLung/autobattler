import pygame
import os

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slashing Animation Example")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# --- Sprite Layers (for drawing order) ---
# Lower numbers are drawn first (at the bottom), higher numbers are drawn last (on top)
PLAYER_LAYER = 2
ENEMY_LAYER = 1
ATTACK_ANIMATION_LAYER = 3  # Ensure attack animation is on top


# --- Helper function to create placeholder images if assets are missing ---
def create_placeholder_image(size, color, text=""):
    """Creates a simple colored surface with optional text."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color + (100,))  # Add some transparency
    font = pygame.font.Font(None, 20)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(text_surf, text_rect)
    return surface


# --- Load Assets ---
# In a real game, you would load actual image files.
# For this example, we'll create simple procedural "slash" frames.
def load_slash_frames():
    frames = []
    # Create 5 frames for a simple slash animation
    for i in range(5):
        frame_size = (80, 80)
        frame_surface = pygame.Surface(frame_size, pygame.SRCALPHA)  # SRCALPHA for transparency

        # Draw a simple diagonal line for the slash
        color_intensity = int(255 * (i + 1) / 5)  # Fade in/out effect
        slash_color = (255, color_intensity, 0, 200)  # Orange-ish, semi-transparent

        # Draw a thick line that changes appearance
        start_pos = (0, frame_size[1] - (i * 10))
        end_pos = (frame_size[0], (i * 10))
        pygame.draw.line(frame_surface, slash_color, start_pos, end_pos, 10 + i * 2)  # Thicker as it progresses

        frames.append(frame_surface)
    return frames


SLASH_ANIMATION_FRAMES = load_slash_frames()


# --- Sprite Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._layer = PLAYER_LAYER  # Assign layer for LayeredUpdates
        self.image = create_placeholder_image((50, 50), BLUE, "Player")
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True  # Direction for attack animation

    def update(self):
        # Simple movement for demonstration
        keys = pygame.key.get_pressed()
        speed = 5
        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
            self.facing_right = True
        if keys[pygame.K_UP]:
            self.rect.y -= speed
        if keys[pygame.K_DOWN]:
            self.rect.y += speed

        # Keep player on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def attack(self, target_rect):
        """Triggers a slashing animation."""
        # Create an instance of the attack animation
        slash_anim = AttackAnimation(
            attacker_rect=self.rect,
            target_rect=target_rect,  # Pass the target's rect for positioning
            animation_frames=SLASH_ANIMATION_FRAMES,
            duration_ms=200,  # Fast slash
            facing_right=self.facing_right
        )
        all_sprites.add(slash_anim)  # Add to the main group for drawing and updating


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._layer = ENEMY_LAYER  # Assign layer for LayeredUpdates
        self.image = create_placeholder_image((40, 40), RED, "Enemy")
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Enemies don't move in this simple example
        pass


class AttackAnimation(pygame.sprite.Sprite):
    def __init__(self, attacker_rect, target_rect, animation_frames, duration_ms, facing_right):
        super().__init__()
        self._layer = ATTACK_ANIMATION_LAYER  # Ensure this is drawn on top

        self.frames = animation_frames
        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        self.rect = self.image.get_rect()

        self.start_time = pygame.time.get_ticks()
        self.duration_ms = duration_ms

        self.attacker_rect = attacker_rect
        self.target_rect = target_rect
        self.facing_right = facing_right

        # Initial positioning of the slash
        self.position_slash()

    def position_slash(self):
        """
        Positions the slash animation relative to the attacker's current position
        and facing direction. This makes it appear "over" or near the attacker.
        """
        # Example positioning:
        # If facing right, slash appears to the right of the attacker's center
        # If facing left, slash appears to the left of the attacker's center

        offset_x = self.attacker_rect.width // 2 + 10  # Offset from attacker's edge

        if self.facing_right:
            self.rect.midleft = self.attacker_rect.midright  # Align midleft of slash with midright of attacker
            self.rect.x += 5  # Push slightly further out
        else:
            # Flip the initial image if facing left
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect.midright = self.attacker_rect.midleft  # Align midright of slash with midleft of attacker
            self.rect.x -= 5  # Push slightly further out

        # Vertically center the slash with the attacker
        self.rect.centery = self.attacker_rect.centery

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time

        # If animation is finished, remove itself from groups
        if elapsed_time >= self.duration_ms:
            self.kill()
            return

        # Determine current frame based on animation progress
        progress = elapsed_time / self.duration_ms
        self.current_frame_index = int(progress * len(self.frames))

        # Ensure index doesn't go out of bounds due to floating point
        if self.current_frame_index >= len(self.frames):
            self.current_frame_index = len(self.frames) - 1

        self.image = self.frames[self.current_frame_index]

        # Re-apply flip if facing left (because image changes each frame)
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Optional: Adjust position slightly during animation for a "swing" effect
        # For example, move the slash slightly forward then back
        # swing_offset = math.sin(progress * math.pi) * 20 # Swing 20 pixels forward and back
        # if self.facing_right:
        #     self.rect.x = self.attacker_rect.midright[0] + 5 + swing_offset
        # else:
        #     self.rect.x = self.attacker_rect.midleft[0] - 5 - swing_offset
        # self.rect.centery = self.attacker_rect.centery


# --- Game Setup ---
all_sprites = pygame.sprite.LayeredUpdates()  # Use LayeredUpdates for z-ordering

player = Player(150, 200)
enemy1 = Enemy(400, 200)
enemy2 = Enemy(600, 300)

all_sprites.add(enemy1, enemy2, player)  # Add in any order, LayeredUpdates handles drawing

# --- Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Trigger attack animation on spacebar press
                # For simplicity, let's target enemy1's rect for positioning reference
                player.attack(enemy1.rect)

    # Update all sprites
    all_sprites.update()

    # Drawing
    SCREEN.fill(BLACK)  # Clear screen
    all_sprites.draw(SCREEN)  # Draw all sprites in their correct layers
    pygame.display.flip()

    clock.tick(60)  # Cap frame rate at 60 FPS

pygame.quit()
