import os
from rl import libtcodpy as libtcod
import rl
import pygame

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

# actual size of the window in cells
SCREEN_WIDTH = 40
SCREEN_WIDTH_HALF = SCREEN_WIDTH / 2
SCREEN_HEIGHT = 24
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT / 2

# size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 48

# parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

TILE_SIZE = 24
tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
tile_wall = pygame.Rect(6 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
tile_floor = pygame.Rect(0 * TILE_SIZE, 0 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

SPRITE_SIZE = 24
sprite_human = pygame.Rect(0, 9 * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)

# actual size of the window in pixels
size = width, height = SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE
pygame.init()
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
wait = 0

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
        images[k] =  pygame.image.load(prefix + v)
    return images

images = load_images(manifest)
tileset_lit = images['world']
tileset_unlit = tileset_lit.copy()
light_intensity  = 128
tileset_unlit.fill((light_intensity, light_intensity, light_intensity), None, pygame.BLEND_MULT)
human_img = images['creatures']

# FOV constants
FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
LIGHT_RADIUS = 10

# OBJECTS

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.

    def __init__(self, x, y, image, rect):
        self.x = x
        self.y = y
        self.image = image
        self.rect = rect
        self.flip = False

    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy


# CAMERA & RENDERER

class Camera:
    def __init__(self, followee):
        self.followee = followee
        self.x = 0
        self.y = 0

    def update(self):
        self.x = self.followee.x - SCREEN_WIDTH_HALF
        self.y = self.followee.y - SCREEN_HEIGHT_HALF
        self.x = max(0, min(self.x, MAP_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT - SCREEN_HEIGHT))


class Renderer():
    BLACK = (0,0,0)

    def __init__(self, camera):
        self.camera = camera

    def render_map(self, map):
        cam = self.camera
        map_width = len(map); map_height = len(map[0])
        for x in range(max(0, cam.x), min(cam.x + SCREEN_WIDTH, map_width)):
            for y in range(max(0, cam.y), min(cam.y + SCREEN_HEIGHT, map_height)):
                if libtcod.map_is_in_fov(fov_map, x, y):
                    img = tileset_lit
                    map[x][y].explored = True
                elif map[x][y].explored:
                    img  = tileset_unlit
                else: continue
                if map[x][y].block_sight:
                    rect = tile_wall
                else:
                    rect = tile_floor
                screen.blit(img, ((x - cam.x) * TILE_SIZE, (y - cam.y) * TILE_SIZE), rect)

    def render_objects(self, objects):
        cam = self.camera
        for object in objects:
            img = pygame.transform.flip(object.image, object.flip, False)
            screen.blit(img, ((object.x - cam.x) * TILE_SIZE,
                              (object.y - cam.y) * TILE_SIZE), object.rect)

    def render(self, map, objects):
        screen.fill(self.BLACK)
        self.render_map(map)
        self.render_objects(objects)
        pygame.display.flip()

# INPUT

def handle_keys():
    global fov_recompute
    global wait
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or \
               event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.has_moved = True
                player.is_moving = True

    # movement keys
    keys = pygame.key.get_pressed()
    if wait <= 0 and player.is_moving:
        dx = dy = 0
        if keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_DOWN]: dy = 1
        elif keys[pygame.K_LEFT]: dx = -1; player.flip = False
        elif keys[pygame.K_RIGHT]: dx = 1; player.flip = True
        if dx or dy:
            player.move(dx, dy)
            libtcod.map_compute_fov(fov_map, player.x, player.y, LIGHT_RADIUS,
                                    FOV_LIGHT_WALLS, FOV_ALGO)

    elif not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and \
         not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        player.is_moving = False
        wait = 0

    if player.has_moved:
        wait = 250
        player.has_moved = False
    elif player.is_moving and wait <= 0:
        wait = 100

    wait -= clock.tick()


# INITIALIZATION & MAIN LOOP

# create object representing the player
player = Object(0, 0, human_img, sprite_human)
player.has_moved = False
player.is_moving = False

# the list of objects with those two
objects = [player]

# generate map (at this point it's not drawn to the screen)
map, fov_map, rooms = rl.map.make_map(MAP_WIDTH, MAP_HEIGHT, \
                      MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
(new_x, new_y) = rooms[0].center()
player.x = new_x
player.y = new_y
libtcod.map_compute_fov(fov_map, player.x, player.y, LIGHT_RADIUS,
                        FOV_LIGHT_WALLS, FOV_ALGO)


camera = Camera(player)
renderer = Renderer(camera)

exit = False
while not exit:
    # handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        pygame.quit()
        break

    # render the screen
    camera.update()
    renderer.render(map, objects)    
