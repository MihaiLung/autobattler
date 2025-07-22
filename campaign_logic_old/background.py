import math

import pygame
import random

from settings import CHUNK_SIZE
from campaign_logic.settlement import Settlement, orc_settlement, elf_settlement, Shadow


def read_in_image(loc):
    image = pygame.image.load(loc).convert_alpha()
    max_side = max(image.get_width(), image.get_height())
    image = pygame.transform.smoothscale(image, (image.get_width() / max_side * 100, image.get_height() / max_side * 100))
    return image


class Grass(pygame.sprite.Sprite):
    GRASS_OPTIONS = [
        read_in_image(f"../assets/grass/grass{i}.png") for i in range(1, 6)
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(self.GRASS_OPTIONS)
        self.rect = self.image.get_rect()
        self.level = 2
        self.chunk_location: pygame.Vector2 = pygame.Vector2(0,0)

    def randomize_chunk_location(self, width, height):
        self.chunk_location = pygame.Vector2(
            random.randint(0, width-self.rect.width),
            random.randint(0, height-self.rect.height)
        )



class BackgroundChunk(pygame.sprite.Sprite):
    GREEN = 151, 186, 134
    SETTLEMENTS = [orc_settlement, elf_settlement]
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((1000, 1000))
        self.image.fill(BackgroundChunk.GREEN)
        self.rect = self.image.get_rect()
        # self.add_grass(random.randint(15,30))
        self.settlement = None
        self.level = 1

        self.initialize()

    def initialize(self):
        # Small chance of settlement
        if random.random() < 0.1:
            self.add_grass(random.randint(2, 5))
            self.settlement = random.choice(BackgroundChunk.SETTLEMENTS)
            shadow = Shadow(self.settlement)
            self.image.blit(shadow.image, (303,297))
            self.image.blit(self.settlement.image, (300, 300))
        else:
            self.add_grass(random.randint(15, 30))

    def add_grass(self, num_grass):
        grasses = []
        for i in range(num_grass):
            new_grass = Grass()
            new_grass.randomize_chunk_location(self.rect.width, self.rect.height)
            grasses.append(new_grass)
        grasses = sorted(grasses, key=lambda grass: grass.chunk_location.y)
        for grass in grasses:
            self.image.blit(grass.image, grass.chunk_location)


def vector_to_closest_chunk(vector: pygame.Vector2) -> tuple[int, int]:
    return math.floor(vector.x/CHUNK_SIZE)*CHUNK_SIZE, math.floor(vector.y/CHUNK_SIZE)*CHUNK_SIZE


class BackgroundChunks(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.chunks = {}
        self.image = pygame.Surface((CHUNK_SIZE*3, CHUNK_SIZE*3))
        self.rect = pygame.Rect(0, 0, CHUNK_SIZE*3, CHUNK_SIZE*3)
        self.player = player
        self.current_center_chunk = self.get_chunk_coords_containing_player()
        self.level=2
        self.refresh_background()

    def get_chunk_coords_containing_player(self):
        return vector_to_closest_chunk(self.player.position)

    def coords_of_chunks_to_render_at_current_position(self):
        closest_chunk = self.get_chunk_coords_containing_player()
        chunks_to_render = []
        for x in [closest_chunk[0]-CHUNK_SIZE, closest_chunk[0], closest_chunk[0]+CHUNK_SIZE]:
            for y in [closest_chunk[1]-CHUNK_SIZE, closest_chunk[1], closest_chunk[1]+CHUNK_SIZE]:
                chunks_to_render.append((x, y))
        return chunks_to_render

    def refresh_background(self):
        chunks_to_render = self.coords_of_chunks_to_render_at_current_position()
        min_x, min_y = chunks_to_render[0]
        print(chunks_to_render[0])
        for chunk_coords in chunks_to_render:
            if chunk_coords not in self.chunks:
                self.chunks[chunk_coords] = BackgroundChunk()
            self.image.blit(self.chunks[chunk_coords].image, (chunk_coords[0]-min_x, chunk_coords[1]-min_y))
        self.rect.topleft = (min_x, min_y)


    def update(self):
        if self.get_chunk_coords_containing_player()!=self.current_center_chunk:
            self.refresh_background()
            self.current_center_chunk = self.get_chunk_coords_containing_player()
