import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((550, 300))
FONT = pygame.font.SysFont(None, 22)


class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, color, health, attack):
        super().__init__()
        self.image_raw = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.image_raw.fill(color)
        pygame.draw.circle(self.image_raw, color, (20, 20), 20)
        self.image = self.image_raw.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.attack = attack
        self.update_image()

    def update_image(self):
        self.image = self.image_raw.copy()
        health_surf = FONT.render(str(self.health), True, (255, 0, 0))
        attack_surf = FONT.render(str(self.attack), True, (0, 0, 0))
        self.image.blit(health_surf, (2, self.image.get_height() - health_surf.get_height() - 2))
        self.image.blit(attack_surf, (self.image.get_width() - attack_surf.get_width() - 2,
                                      self.image.get_height() - attack_surf.get_height() - 2))

    def draw(self, surface, offset=(0, 0)):
        # offset is (camera_x, camera_y)
        pos = self.rect.move(-offset[0], -offset[1])
        surface.blit(self.image, pos)


class Orc(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (90, 180, 60), 12, 8)


class Elf(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (60, 120, 180), 9, 10)


# Camera class
class Camera:
    def __init__(self, width, height):
        self.pos = pygame.Vector2(0, 0)
        self.width = width
        self.height = height

    def center_on(self, target_rect):
        self.pos.x = target_rect.centerx - self.width // 2
        self.pos.y = target_rect.centery - self.height // 2


# Closest function
def find_closest(source_group, target_group):
    pairings = {}
    for s in source_group:
        # Find t in target_group with min distance to s
        min_t = min(target_group,
                    key=lambda t: (s.rect.centerx - t.rect.centerx) ** 2 + (s.rect.centery - t.rect.centery) ** 2)
        pairings[s] = min_t
    return pairings


# --- Demo setup ---

orc_group = pygame.sprite.Group()
elf_group = pygame.sprite.Group()
for _ in range(5):
    orc_group.add(Orc(random.randint(50, 450), random.randint(50, 250)))
    elf_group.add(Elf(random.randint(50, 450), random.randint(50, 250)))

orc_camera = Camera(275, 300)  # Each camera - half the screen width
elf_camera = Camera(275, 300)

running = True
clock = pygame.time.Clock()
selected_orc = next(iter(orc_group))
selected_elf = next(iter(elf_group))
frame = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Center each camera on first orc/elf for demo
    orc_camera.center_on(selected_orc.rect)
    elf_camera.center_on(selected_elf.rect)

    # --- Compute nearests ---
    orc_to_elf = find_closest(orc_group, elf_group)
    elf_to_orc = find_closest(elf_group, orc_group)
    # (You could, for example, highlight these or draw lines)

    screen.fill((30, 30, 30))

    # Draw orc's camera view (left)
    orc_view = pygame.Surface((275, 300))
    orc_view.fill((30, 30, 30))
    for orc in orc_group:
        orc.draw(orc_view, orc_camera.pos)
    for elf in elf_group:
        elf.draw(orc_view, orc_camera.pos)
    # (optionally, draw lines from each orc to their closest elf)
    for orc, closest_elf in orc_to_elf.items():
        ox, oy = orc.rect.centerx - orc_camera.pos.x, orc.rect.centery - orc_camera.pos.y
        ex, ey = closest_elf.rect.centerx - orc_camera.pos.x, closest_elf.rect.centery - orc_camera.pos.y
        pygame.draw.line(orc_view, (255, 255, 0), (ox, oy), (ex, ey), 1)
    screen.blit(orc_view, (0, 0))

    # Draw elf's camera view (right)
    elf_view = pygame.Surface((275, 300))
    elf_view.fill((30, 30, 30))
    for orc in orc_group:
        orc.draw(elf_view, elf_camera.pos)
    for elf in elf_group:
        elf.draw(elf_view, elf_camera.pos)
    # (optionally, draw lines from each elf to their closest orc)
    for elf, closest_orc in elf_to_orc.items():
        ex, ey = elf.rect.centerx - elf_camera.pos.x, elf.rect.centery - elf_camera.pos.y
        ox, oy = closest_orc.rect.centerx - elf_camera.pos.x, closest_orc.rect.centery - elf_camera.pos.y
        pygame.draw.line(elf_view, (255, 0, 255), (ex, ey), (ox, oy), 1)
    screen.blit(elf_view, (275, 0))

    pygame.display.flip()
    clock.tick(60)
    frame += 1
pygame.quit()