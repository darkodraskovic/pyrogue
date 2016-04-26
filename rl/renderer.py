import libtcodpy as libtcod
import pygame

class Renderer():
    BLACK = (0,0,0)

    def __init__(self, screen, camera, tile_size):
        self.camera = camera
        self.tile_size = tile_size
        self.screen = screen

    def render_tiles(self, map):
        cam = self.camera
        data = map['data']
        fov_map = map['fov_map']
        map_width = len(data); map_height = len(data[0])
        for x in range(max(0, cam.x), min(cam.x + cam.scr_w, map_width)):
            for y in range(max(0, cam.y), min(cam.y + cam.scr_h, map_height)):
                if libtcod.map_is_in_fov(fov_map, x, y):
                    img = tileset_lit
                    data[x][y].explored = True
                elif data[x][y].explored:
                    img  = tileset_unlit
                else: continue
                if data[x][y].block_sight:
                    rect = tile_wall
                else:
                    rect = tile_floor
                self.screen.blit(img, ((x - cam.x) * self.tile_size, (y - cam.y) * self.tile_size), rect)

    def render_objects(self, map):
        cam = self.camera
        objects = map['objects']
        fov_map = map['fov_map']        
        for object in objects:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                img = pygame.transform.flip(object.image, object.flip, False)
                self.screen.blit(img, ((object.x - cam.x) * self.tile_size,
                                  (object.y - cam.y) * self.tile_size))

    def render(self, map):
        self.screen.fill(self.BLACK)
        self.render_tiles(map)
        self.render_objects(map)
        pygame.display.flip()
