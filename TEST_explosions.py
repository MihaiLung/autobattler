import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, speed_min, speed_max, size_min, size_max, lifetime):
        self.x = x
        self.y = y
        self.color = list(color) # Convert to list to allow modification (e.g., fading)
        self.size = random.randint(size_min, size_max)
        self.lifetime = lifetime # How many frames or milliseconds the particle exists
        self.current_lifetime = lifetime

        # Random direction and speed
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(speed_min, speed_max)
        self.velocity_x = speed * math.cos(angle)
        self.velocity_y = speed * math.sin(angle)

        self.alpha = 255 # For fading
        self.fade_rate = 255 / lifetime # How much alpha to decrease per frame

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Apply a small amount of "gravity" or drag
        self.velocity_y += 0.1 # Example: small downward pull
        self.velocity_x *= 0.99 # Example: slight air resistance

        # Fade out the particle
        self.alpha -= self.fade_rate
        if self.alpha < 0:
            self.alpha = 0
        self.color[3] = int(self.alpha) # Update alpha in the color tuple

        self.current_lifetime -= 1

    def draw(self, surface):
        if self.current_lifetime > 0:
            # Use pygame.SRCALPHA to draw with transparency
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size),  )

class Explosion:
    def __init__(self, x, y, num_particles, color, speed_range, size_range, lifetime):
        self.particles = []
        for _ in range(num_particles):
            self.particles.append(
                Particle(x, y, color, speed_range[0], speed_range[1],
                         size_range[0], size_range[1], lifetime)
            )
        self.active = True

    def update(self):
        for particle in self.particles:
            particle.update()

        # Remove dead particles
        self.particles = [p for p in self.particles if p.current_lifetime > 0 and p.alpha > 0]

        if not self.particles: # If no particles are left, the explosion is done
            self.active = False

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Pygame Explosion")

clock = pygame.time.Clock()
FPS = 60

explosions = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Create an explosion at mouse click
            ex_x, ex_y = event.pos
            explosions.append(
                Explosion(ex_x, ex_y,
                          num_particles=500,
                          color=(255, 100, 0, 255), # Orange, with full alpha
                          speed_range=(2, 8),
                          size_range=(2, 7),
                          lifetime=120) # Lasts for 60 frames
            )

    screen.fill((30, 30, 30)) # Dark background

    # Update and draw explosions
    for explosion in explosions:
        explosion.update()
        explosion.draw(screen)

    # Remove inactive explosions
    explosions = [e for e in explosions if e.active]

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()