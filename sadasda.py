import pygame
import math

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Physics Collision Simulation")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, mass, color, pos, velocity):
        super().__init__()
        self.radius = radius
        self.mass = mass
        self.color = color
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA) # SRCALPHA for transparency
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Basic wall collisions (reflect velocity)
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity.x *= -1
            # Push back to prevent sticking
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx # Update float position from rect

        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.velocity.y *= -1
            # Push back to prevent sticking
            if self.rect.top < 0: self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.centery # Update float position from rect

def resolve_collision(ball1, ball2, elasticity=1.0):
    """
    Resolves a collision between two circular balls using physics formulas.
    elasticity: 1.0 for perfectly elastic, 0.0 for perfectly inelastic.
    """
    # 1. Get collision normal
    normal = ball1.pos - ball2.pos
    distance = normal.length()

    # Avoid division by zero if centers are identical
    if distance == 0:
        # If they are exactly on top of each other, assign a random normal
        # and slightly separate them to prevent infinite loop.
        normal = pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() % 360)
        distance = 1.0 # arbitrary non-zero value
        print("Warning: Balls at same position, random normal assigned.")

    if distance < ball1.radius + ball2.radius: # Collision detected (and overlap)
        # 2. Resolve overlap
        overlap = (ball1.radius + ball2.radius) - distance
        normal_normalized = normal.normalize()

        # Move balls apart based on mass (lighter moves more)
        total_mass = ball1.mass + ball2.mass
        ball1.pos += normal_normalized * (overlap * (ball2.mass / total_mass))
        ball2.pos -= normal_normalized * (overlap * (ball1.mass / total_mass))

        # Update rect centers after position adjustment
        ball1.rect.center = (int(ball1.pos.x), int(ball1.pos.y))
        ball2.rect.center = (int(ball2.pos.x), int(ball2.pos.y))


        # 3. Calculate initial relative velocity along normal
        relative_velocity = ball1.velocity - ball2.velocity
        velocity_along_normal = relative_velocity.dot(normal_normalized)

        # Only apply impulse if objects are moving towards each other
        if velocity_along_normal > 0:
            return # Already moving apart or parallel, no new impulse needed

        # 4. Calculate impulse magnitude
        # Impulse magnitude formula
        j = -(1 + elasticity) * velocity_along_normal
        j /= (1 / ball1.mass) + (1 / ball2.mass)

        # 5. Apply impulse to update velocities
        impulse_vector = normal_normalized * j

        ball1.velocity += impulse_vector / ball1.mass
        ball2.velocity -= impulse_vector / ball2.mass # Subtract for ball2 as normal points away from it

# --- Main Game Loop ---
all_sprites = pygame.sprite.Group()

# Create some balls
ball1 = Ball(radius=20, mass=1.0, color=RED, pos=(100, 300), velocity=(50, -30))
ball2 = Ball(radius=30, mass=2.0, color=BLUE, pos=(300, 300), velocity=(-20, 10))
ball3 = Ball(radius=25, mass=0.5, color=GREEN, pos=(500, 200), velocity=(-40, 60))

all_sprites.add(ball1, ball2, ball3)

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0 # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update sprite positions
    all_sprites.update(dt)

    # Collision detection and response (nested loop for all pairs)
    sprites_list = all_sprites.sprites()
    num_sprites = len(sprites_list)

    for i in range(num_sprites):
        sprite_a = sprites_list[i]
        for j in range(i + 1, num_sprites): # Avoid self-collision and duplicate pairs
            sprite_b = sprites_list[j]

            # For rectangular sprites using colliderect:
            # if sprite_a.rect.colliderect(sprite_b.rect):
            #     # For simple Rect collision, calculating proper normal and overlap is harder.
            #     # You'd need to determine the axis of least penetration.
            #     # This usually involves SAT (Separating Axis Theorem) for complex shapes.
            #     # For circles, it's straightforward.

            # For circular sprites (like our Ball class):
            distance = sprite_a.pos.distance_to(sprite_b.pos)
            if distance < sprite_a.radius + sprite_b.radius:
                resolve_collision(sprite_a, sprite_b, elasticity=0.9) # Adjust elasticity (0.0 to 1.0)

    # Drawing
    screen.fill((30, 30, 30)) # Dark grey background
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()