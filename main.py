import rl
from rl import gui
from rl import sprite
from rl import camera
from rl import renderer
from rl import map as rl_map

import pygame
from settings import Settings
import game
import tilemap
import entity

settings = Settings()

# Camera & renderer
renderer = renderer.Renderer(
    settings.SCREEN_WIDTH * settings.TILE_SIZE,
    settings.SCREEN_HEIGHT * settings.TILE_SIZE,
    settings.SCALE,
)

pygame.init()
pygame.font.init()

prefix = "assets/images/"
manifest = {
    "creatures": "creatures.png",
    "creatures_extra": "creatures_extra.png",
    "FX": "FX.png",
    "items": "items.png",
    "vehicles": "vehicles.png",
    "world": "world.png",
    "world_decals": "world_decals.png",
}


# graphics
def load_images(manifest):
    images = {}
    for k, v in manifest.items():
        images[k] = (pygame.image.load(prefix + v)).convert_alpha()
    return images


images = load_images(manifest)

# INITIALIZATION & MAIN LOOP

# generate map
map = rl_map.make_map(
    settings.MAP_WIDTH,
    settings.MAP_HEIGHT,
    settings.MAX_ROOMS,
    settings.ROOM_MIN_SIZE,
    settings.ROOM_MAX_SIZE,
)
tilemap = tilemap.Tilemap(map, settings.TILE_SIZE, images["world"], 127)

tile_wall = pygame.Rect(
    6 * settings.TILE_SIZE,
    0 * settings.TILE_SIZE,
    settings.TILE_SIZE,
    settings.TILE_SIZE,
)
tile_floor = pygame.Rect(
    0 * settings.TILE_SIZE,
    0 * settings.TILE_SIZE,
    settings.TILE_SIZE,
    settings.TILE_SIZE,
)

data = map["data"]
for row in data:
    for tile in row:
        if tile.block_sight:
            tile.rect = tile_wall
        else:
            tile.rect = tile_floor


# generate player
creatures_anim_sheet = sprite.AnimSheet(images["creatures"], 24, 24)


player = rl.map.place_object(
    map, 0, entity.Player, "player", creatures_anim_sheet, 288, True
)
player.compute_fov()
player.set_anim("idle", [288, 289])
player.use_anim("idle")


# generate other entities
objs = rl.map.place_objects(
    map, 0, entity.Monster, 2, 4, "monster", creatures_anim_sheet, 384, True, player
)

objs = [player] + objs
object_group = pygame.sprite.Group(*objs)
objs2 = [tilemap, player] + objs
update_group = pygame.sprite.LayeredDirty(*objs2)

# Gui

ts = settings.TILE_SIZE * settings.SCALE
p_w = settings.SCREEN_WIDTH * ts
p_h = ts
p_rect = pygame.Rect((0, 0), (p_w, p_h))
p_col_fill = (64, 64, 196, 127)
p_col_stroke = (128, 128, 196, 127)

panel = gui.Panel(
    0, 0, rect=p_rect, fill=p_col_fill, stroke=p_col_stroke, stroke_size=3
)
text = gui.Text(
    0, 0, parent=panel, padding=4, text="Text", color=(162, 162, 162), size=32
)
gui_group = pygame.sprite.LayeredDirty(panel, text)

camera = camera.Camera(
    player,
    settings.SCREEN_WIDTH * settings.TILE_SIZE,
    settings.SCREEN_HEIGHT * settings.TILE_SIZE,
    settings.MAP_WIDTH * settings.TILE_SIZE,
    settings.MAP_HEIGHT * settings.TILE_SIZE,
)

while 1:
    game.update(player, camera.x, camera.y, update_group, object_group)
    text.set_text(
        "HP: "
        + str(player.components["fighter"].hp)
        + "/"
        + str(player.components["fighter"].max_hp)
    )
    # render the screen
    camera.update()
    renderer.update(update_group, gui_group)
