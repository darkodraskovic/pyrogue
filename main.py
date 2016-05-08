import rl
from rl import libtcodpy as libtcod
from rl import gui
from rl import sprite
from rl import camera
from rl import renderer
import pygame
from settings import *
import game
import tilemap
import entity

# Camera & renderer
renderer = renderer.Renderer(SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE, SCALE)

pygame.init()

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

camera = camera.Camera(player, SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE,
                MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)

while 1:
    game.update(player, camera.x, camera.y, update_group, object_group)
    text.set_text('HP: ' + str(player.components['fighter'].hp) + '/' +\
                  str(player.components['fighter'].max_hp))    
    # render the screen
    camera.update()
    renderer.update(update_group, gui_group)
