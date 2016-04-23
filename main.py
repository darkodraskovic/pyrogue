import os
import libtcodpy as libtcod
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

# graphics
BLACK = (0,0,0)
tileset_lit = pygame.image.load("assets/tileset.png")
tileset_unlit = tileset_lit.copy()
light_intensity  = 128
tileset_unlit.fill((light_intensity, light_intensity, light_intensity), None, pygame.BLEND_MULT)
human_img = pygame.image.load("assets/human.png")

# FOV constants
FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
LIGHT_RADIUS = 10

# MAP

class Rect:

    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:

    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight
        self.explored = False


def create_room(room):
    global map
    # go through the tiles in the rectangle and make them passable
    # leave some walls at the border of the room
    # Python's range function excludes the last element in the loop
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global map
    # vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def make_map():
    global map, player

    # fill map with "blocked" tiles
    map = [[Tile(True)
            for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        # random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        # random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        # "Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        # run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # this means there are no intersections, so this room is valid

            # "paint" it to the map's tiles
            create_room(new_room)

            # center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                # this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                # all rooms after the first:
                # connect it to the previous room with a tunnel

                # center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            # finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1


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


# RENDERER

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


def render(cam):
    screen.fill(BLACK)
    global fov_recompute
    
    if fov_recompute:
        # recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, LIGHT_RADIUS,
                                FOV_LIGHT_WALLS, FOV_ALGO)
        
    for x in range(max(0, cam.x), min(cam.x + SCREEN_WIDTH, MAP_WIDTH)):
        for y in range(max(0, cam.y), min(cam.y + SCREEN_HEIGHT, MAP_HEIGHT)):
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

    # draw all objects in the list
    for object in objects:
        img = pygame.transform.flip(object.image, object.flip, False)
        screen.blit(img, ((object.x - cam.x) * TILE_SIZE,
                          (object.y - cam.y) * TILE_SIZE), object.rect)

    pygame.display.flip()

# INPUT

fov_recompute = True

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
        if keys[pygame.K_UP]:
            player.move(0, -1)
            fov_recompute = True
        elif keys[pygame.K_DOWN]:
            player.move(0, 1)
            fov_recompute = True
        elif keys[pygame.K_LEFT]:
            player.move(-1, 0)
            fov_recompute = True
            player.flip = False
        elif keys[pygame.K_RIGHT]:
            player.move(1, 0)
            fov_recompute = True
            player.flip = True
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
make_map()

# FOV
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y,
                                   not map[x][y].block_sight, not map[x][y].blocked)

camera = Camera(player)

exit = False
while not exit:
    # handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        pygame.quit()
        break

    # render the screen
    camera.update()
    render(camera)    
