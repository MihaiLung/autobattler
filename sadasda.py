import pygame
import math



# --- Example Usage ---
if __name__ == '__main__':
    pygame.init()

    # Screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Weapon Swing Example")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)

    # --- Create a dummy weapon image (pointing up) ---
    weapon_width = 20
    weapon_height = 80
    weapon_surface = pygame.Surface((weapon_width, weapon_height), pygame.SRCALPHA)
    pygame.draw.rect(weapon_surface, (150, 75, 0), (0, weapon_height - 20, weapon_width, 20)) # Handle
    pygame.draw.polygon(weapon_surface, (100, 100, 100), [(0, weapon_height - 20), (weapon_width, weapon_height - 20), (weapon_width / 2, 0)]) # Blade
    # Draw a small circle at the assumed pivot point (bottom center)
    pygame.draw.circle(weapon_surface, (255, 0, 0), (weapon_width // 2, weapon_height), 3)

    # --- Player/Origin Setup ---
    player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    player_size = 50
    player_rect = pygame.Rect(0, 0, player_size, player_size)
    player_rect.center = player_pos

    all_sprites = pygame.sprite.Group()
    swing_sprites = pygame.sprite.Group() # Group specifically for swings

    # --- Game Loop ---
    running = True
    clock = pygame.time.Clock()

    print("Press SPACE to trigger a swing (0 degrees = right)")
    print("Press D to trigger a swing (90 degrees = down)")
    print("Press A to trigger a swing (180 degrees = left)")
    print("Press W to trigger a swing (270 degrees = up)")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Swing to the right (center of arc is 0 degrees)
                    new_swing = WeaponSwing(player_pos, player_rect, 0, weapon_surface)
                    swing_sprites.add(new_swing)
                    all_sprites.add(new_swing)
                elif event.key == pygame.K_d:
                    # Swing downwards (center of arc is 90 degrees)
                    new_swing = WeaponSwing(player_pos, player_rect, 90, weapon_surface)
                    swing_sprites.add(new_swing)
                    all_sprites.add(new_swing)
                elif event.key == pygame.K_a:
                    # Swing to the left (center of arc is 180 degrees)
                    new_swing = WeaponSwing(player_pos, player_rect, 180, weapon_surface)
                    swing_sprites.add(new_swing)
                    all_sprites.add(new_swing)
                elif event.key == pygame.K_w:
                    # Swing upwards (center of arc is 270 degrees)
                    new_swing = WeaponSwing(player_pos, player_rect, 270, weapon_surface)
                    swing_sprites.add(new_swing)
                    all_sprites.add(new_swing)

        # --- Update ---
        all_sprites.update()

        # --- Drawing ---
        screen.fill(WHITE)

        # Draw the player/origin rect
        pygame.draw.rect(screen, BLUE, player_rect, 2) # Border only
        pygame.draw.circle(screen, (0, 0, 150), player_pos, 5) # Mark origin point

        # Draw the swing sprites
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()