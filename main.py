import os
from rl import libtcodpy as libtcod
import rl
from rl import kbd
import pygame

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

# actual size of the window in cells
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 24

# size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 48

# parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

TILE_SIZE = 24
tile_wall = pygame.Rect(6 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
tile_floor = pygame.Rect(0 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

# actual size of the window in pixels
size = width, height = SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE
pygame.init()
screen = pygame.display.set_mode(size)


clock = pygame.time.Clock()
wait = 0
PA_IDLE = 0
PA_TURN = 1

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
# tiles
tileset_lit = images['world']
tileset_unlit = tileset_lit.copy()
light_intensity  = 128
tileset_unlit.fill((light_intensity, light_intensity, light_intensity), None, pygame.BLEND_MULT)
# entities
img_animes = images['creatures']

# FOV constants
FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
LIGHT_RADIUS = 10

# OBJECTS

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, name, image, blocks=False):
        self.x = x
        self.y = y
        self.name = name
        self.blocks = blocks
        self.image = image
        self.flip = False

    def move(self, map, dx, dy):
        # move by the given amount, if the destination is not blocked
        # if not map[self.x + dx][self.y + dy].blocked:
        if not rl.map.is_blocked(map, self.x+dx, self.y+dy):
            self.x += dx
            self.y += dy

# CAMERA & RENDERER

class Camera:
    def __init__(self, followee, scr_w, scr_h, map_w, map_h):
        self.x = 0
        self.y = 0
        self.followee = followee
        self.scr_w = scr_w
        self.scr_h = scr_h
        self.map_w = map_w
        self.map_h = map_h

    def update(self):
        self.x = self.followee.x - self.scr_w/2
        self.y = self.followee.y - self.scr_h/2
        self.x = max(0, min(self.x, self.map_w - self.scr_w))
        self.y = max(0, min(self.y, self.map_h - self.scr_h))


class Renderer:
    BLACK = (0,0,0)

    def __init__(self, camera, tile_size):
        self.camera = camera
        self.tile_size = tile_size

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
                screen.blit(img, ((x - cam.x) * self.tile_size, (y - cam.y) * self.tile_size), rect)

    def render_objects(self, map):
        cam = self.camera
        objects = map['objects']
        fov_map = map['fov_map']        
        for object in objects:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                img = pygame.transform.flip(object.image, object.flip, False)
                screen.blit(img, ((object.x - cam.x) * self.tile_size,
                                  (object.y - cam.y) * self.tile_size))

    def render(self, map):
        screen.fill(self.BLACK)
        self.render_tiles(map)
        self.render_objects(map)
        pygame.display.flip()

# INPUT
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4
EXIT = 5

kbd.bind_key(pygame.K_UP, UP); kbd.bind_key(pygame.K_w, UP)
kbd.bind_key(pygame.K_DOWN, DOWN); kbd.bind_key(pygame.K_s, DOWN)
kbd.bind_key(pygame.K_LEFT, LEFT); kbd.bind_key(pygame.K_a, LEFT)
kbd.bind_key(pygame.K_RIGHT, RIGHT); kbd.bind_key(pygame.K_d, RIGHT)
kbd.bind_key(pygame.K_ESCAPE, EXIT)

def handle_keys(map, player):
    global wait

    kbd.handle_keys()

    for event in pygame.event.get():
        if event.type == kbd.KEYDOWN:
            if event.action == EXIT:
                return 'exit'
            else:
                Game.player_action = Game.PA_TURN
                Game.game_state = Game.GS_BUSY
                wait = 250

    if not kbd.is_pressed_any():
        Game.game_state = Game.GS_IDLE

    if Game.player_action == PA_TURN:
        dx = dy = 0
        if kbd.is_pressed(UP): dy = -1
        elif kbd.is_pressed(DOWN): dy = +1
        elif kbd.is_pressed(LEFT): dx = -1; player.flip = False
        elif kbd.is_pressed(RIGHT): dx = +1; player.flip = True
        if dx or dy:
            player.move(map, dx, dy)
            libtcod.map_compute_fov(map['fov_map'], player.x, player.y, LIGHT_RADIUS,
                                    FOV_LIGHT_WALLS, FOV_ALGO)
        Game.player_action = PA_IDLE
        Game.turn_count += 1

    if Game.game_state == Game.GS_BUSY:
        if wait <= 0:
            Game.player_action = Game.PA_TURN
            wait = 100

class Game:
    GS_IDLE = 0
    GS_BUSY = 1
    GS_EXIT = 2
    PA_IDLE = 0
    PA_TURN = 1
    game_state = GS_IDLE
    player_action = PA_IDLE
    turn_count = 0

    @staticmethod
    def update(map, player):
        handle_keys(map, player)
        
        if Game.game_state == 'playing' and Game.player_action != 'didnt-take-turn':
            for object in map['objects']:
                print 'The ' + object.name + ' says "Hello!"'


# INITIALIZATION & MAIN LOOP

# generate map
map  = rl.map.make_map(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

# generate player
img = img_animes.subsurface((0*TILE_SIZE, 9*TILE_SIZE, TILE_SIZE, TILE_SIZE))
player = Object(0, 0, "player", img, True)
(new_x, new_y) = map['rooms'][0].center()
player.x = new_x
player.y = new_y
map['objects'].append(player)
libtcod.map_compute_fov(map['fov_map'], player.x, player.y, LIGHT_RADIUS,
                        FOV_LIGHT_WALLS, FOV_ALGO)

# generate objects
img = img_animes.subsurface((0*TILE_SIZE, 12*TILE_SIZE, TILE_SIZE, TILE_SIZE))
rl.map.place_objects(map, 0, Object, 2, 4, "friend", img, True)

camera = Camera(player, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
renderer = Renderer(camera, TILE_SIZE)

exit = False
while Game.game_state != Game.GS_EXIT:
    # handle keys and exit game if needed
    exit = handle_keys(map, player)
    if exit == 'exit':
        pygame.quit()
        
    Game.update(map, player)
    
    # render the screen
    camera.update()
    renderer.render(map)

    wait -= clock.tick()
