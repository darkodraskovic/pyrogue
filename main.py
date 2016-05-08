import os
import rl
import math
from rl import libtcodpy as libtcod
from rl import gui
from rl import sprite
import pygame
from settings import *
import game
import tilemap
import entity

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

# actual size of the window in pixels
size = width, height = SCREEN_WIDTH * TILE_SIZE * SCALE, SCREEN_HEIGHT * TILE_SIZE * SCALE
pygame.init()
screen = pygame.display.set_mode(size)
screen_buffer = pygame.Surface((width/SCALE, height/SCALE))

prefix = 'assets/images/'
manifest = {
    'creatures': 'creatures.png',
    'creatures_extra': 'creatures_extra.png',
    'FX': 'FX.png',
    'items': 'items.png',
    'vehicles': 'vehicles.png',
    'world': 'world.png',
    'world_decals': 'world_decals.png'
}
# graphics
def load_images(manifest):
    images = {}
    for k,v in manifest.items():
        images[k] = (pygame.image.load(prefix + v)).convert_alpha()
    return images

images = load_images(manifest)

# CAMERA & RENDERER

class Camera:
    def __init__(self, followee, scr_w, scr_h, world_w, world_h):
        self.x = 0
        self.y = 0
        self.followee = followee
        self.translator = self.followee.components['translator']
        self.world_x = self.followee.rect.x
        self.world_y = self.followee.rect.y
        self.scr_w = scr_w
        self.scr_h = scr_h
        self.world_w = world_w
        self.world_h = world_h

    def update(self):
        self.x = self.followee.x - SCREEN_WIDTH/2
        self.y = self.followee.y - SCREEN_HEIGHT/2
        self.x = max(0, min(self.x, MAP_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT - SCREEN_HEIGHT))
        self.world_x = self.translator.x - self.scr_w/2
        self.world_y = self.translator.y - self.scr_h/2
        self.world_x = max(0, min(self.world_x, self.world_w - self.scr_w))
        self.world_y = max(0, min(self.world_y, self.world_h - self.scr_h))

class Renderer:
    BLACK = (0,0,0)
    global screen_buffer

    def render(self):
        screen_buffer.fill(self.BLACK)
        update_group.draw(screen_buffer)
        text.set_text('HP: ' + str(player.components['fighter'].hp) + '/' +\
                      str(player.components['fighter'].max_hp))
        
        rect = screen.get_rect()
        scr = pygame.transform.scale(screen_buffer, (rect.width, rect.height))
        screen.blit(scr, screen.get_rect())
        gui_group.draw(screen)
        pygame.display.flip()

# INITIALIZATION & MAIN LOOP

# generate map
map  = rl.map.make_map(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
tilemap = tilemap.Tilemap(map, TILE_SIZE, images['world'], 127)

tile_wall = pygame.Rect(6 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
tile_floor = pygame.Rect(0 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

data = map['data']
for row in data:
    for tile in row:
        if tile.block_sight:
            tile.rect = tile_wall
        else:
            tile.rect = tile_floor

# generate player
creatures_anim_sheet = sprite.AnimSheet(images['creatures'], 24, 24)

player = rl.map.place_object(map, 0, entity.Player, "player", creatures_anim_sheet, 288,  True)
player.compute_fov()
player.set_anim('idle', [288, 289])
player.use_anim('idle')

# generate other entities
objs = rl.map.place_objects(map, 0, entity.Monster, 2, 4, "monster", creatures_anim_sheet, 384, True, player)

objs = [player] + objs
object_group = pygame.sprite.Group(*objs)
objs2 = [tilemap, player] + objs
update_group = pygame.sprite.LayeredDirty(*objs2)

# Gui

ts = TILE_SIZE * SCALE
p_w = SCREEN_WIDTH * ts
p_h = ts
p_rect = pygame.Rect((0, 0), (p_w, p_h))
p_col_fill = (64, 64, 196, 127)
p_col_stroke = (128, 128, 196, 127)

panel = gui.Panel(0, 0, rect=p_rect, fill=p_col_fill, stroke=p_col_stroke, stroke_size=3)
text = gui.Text(0, 0, parent=panel, padding=4, text="Text", color=(162, 162, 162), size=32)
gui_group = pygame.sprite.LayeredDirty(panel, text)

# Camera & renderer
camera = Camera(player, SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE,
                MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
renderer = Renderer()

while 1:
    game.update(player, camera.world_x, camera.world_y, update_group, object_group)
    
    # render the screen
    camera.update()
    renderer.render()
