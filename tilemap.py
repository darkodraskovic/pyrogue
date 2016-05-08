from rl import libtcodpy as libtcod
import pygame
from rl import sprite
from settings import *

class Tilemap(sprite.Sprite):
    def __init__(self, map, tile_size, tileset, light_intensity=127, x=0, y=0):
        self.map = map
        self.tile_size = tile_size
        self.map_w = len(map['data'])
        self.map_h = len(map['data'][0])
        self.tileset_light = tileset
        self.tileset_dark = tileset.copy()
        self.tileset_dark.fill((light_intensity, light_intensity, light_intensity), None, pygame.BLEND_MULT)

        image = pygame.Surface((self.map_w * tile_size, self.map_h * tile_size)).convert_alpha()
        sprite.Sprite.__init__(self, x, y, image)

    def update(self, dt, viewport_x, viewport_y):
        data = self.map['data']
        fov_map = self.map['fov_map']
        map_x = int(viewport_x / self.tile_size)
        map_y = int(viewport_y / self.tile_size)
        
        self.image.fill((0,0,0))
        for x in range(max(0, map_x-1), min(map_x + SCREEN_WIDTH + 1, self.map_w)):
            for y in range(max(0, map_y-1), min(map_y + SCREEN_HEIGHT + 1, self.map_h)):
                tile = data[x][y]
                if libtcod.map_is_in_fov(fov_map, x, y):
                    tileset = self.tileset_light
                    tile.explored = True
                elif tile.explored:
                    tileset  = self.tileset_dark
                else:
                    continue
                self.image.blit(tileset,
                                (x * self.tile_size - viewport_x, y * self.tile_size - viewport_y),
                                tile.rect)
