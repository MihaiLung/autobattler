import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

# Create original surface: a simple colored circle token
TOKEN_RADIUS = 80
original = pygame.Surface((TOKEN_RADIUS*2, TOKEN_RADIUS*2), pygame.SRCALPHA)
pygame.draw.circle(original, (180, 180, 180), (TOKEN_RADIUS, TOKEN_RADIUS), TOKEN_RADIUS)

# Random rotation angle
angle = random.uniform(-45, 45)

# Rotate original
rotated = pygame.transform.rotate(original, angle)
rotated_rect = rotated.get_rect(center=(0,0))  # keep center at (0,0) for simplicity

# Pick random vertical cut position in rotated space
cut_x = random.randint(rotated.get_width()//3, rotated.get_width()*2//3)

# Create left and right slices
left_slice = rotated.subsurface((0, 0, cut_x, rotated.get_height())).copy()
right_slice = rotated.subsurface((cut_x, 0, rotated.get_width() - cut_x, rotated.get_height())).copy()

# Rotate slices back
left_unrot = pygame.transform.rotate(left_slice, -angle)
right_unrot = pygame.transform.rotate(right_slice, -angle)

# Create empty surface to hold reconstructed image
reconstructed = pygame.Surface(original.get_size(), pygame.SRCALPHA)

# Here's the trick: we need to know where to blit them.
# Since the rotation enlarged the bounding box, we can't just use original positions.

# We'll compute offsets so that, together, they fit into the reconstructed image

# Blit left_unrot centered on the left half
left_rect = left_unrot.get_rect()
left_rect.center = (TOKEN_RADIUS, TOKEN_RADIUS)  # center on token center

# Do the same for right_unrot, but shift it by the difference between cut_x and center
right_rect = right_unrot.get_rect()
right_rect.center = (TOKEN_RADIUS, TOKEN_RADIUS)  # also center

# Blit both onto reconstructed
reconstructed.blit(left_unrot, left_rect)
reconstructed.blit(right_unrot, right_rect)

# Main loop to show result
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30,30,30))

    # Show original on left
    screen.blit(original, (50, 200 - TOKEN_RADIUS))

    # Show reconstructed on right
    screen.blit(reconstructed, (300, 200 - TOKEN_RADIUS))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
