import os
import rl
from rl import libtcodpy as libtcod
from rl import entity
from rl import gui
import pygame
import game

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

# actual size of the window in cells
SCREEN_WIDTH = 36
SCREEN_HEIGHT = 20
SCALE = 2

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

# COMPONENTS

class Fighter(entity.Component):
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, owner, hp, defense_pow, attack_pow):
        entity.Component.__init__(self, owner, "fighter")
        self.max_hp = hp
        self.hp = hp
        self.defense_pow = defense_pow
        self.attack_pow = attack_pow

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

    def attack(self, target):
        damage = self.attack_pow - target.components['fighter'].defense_pow

        attack_str = self.owner.name.capitalize() + ' attacks ' + target.name
        if damage > 0:
            print  attack_str + ' for ' + str(damage) + ' hit points.'
            target.components['fighter'].take_damage(damage)
        else:
            print attack_str + ' but it has no effects.'

class MonsterAI(entity.Component):    
    #AI for a basic monster.
    def __init__(self, owner, target):
        entity.Component.__init__(self, owner, "monster")
        self.target = target
        
    def take_turn(self):
        monster = self.owner
        target = self.target
        if libtcod.map_is_in_fov(monster.map['fov_map'], monster.x, monster.y):
            if monster.distance_to(target.x, target.y) >= 2:
                monster.move_towards(target.x, target.y)
                self.owner.components['translator'].set_destination(self.owner.x, self.owner.y)
            else:
                self.owner.components['fighter'].attack(target)
            

# OBJECTS
class Entity(entity.Object):
    def __init__(self, x, y, name, blocks=False, image=None):
        entity.Object.__init__(self, x, y, name, blocks)
        self.image = image
        self.rect = image.get_rect()
        self.flip = False
        self.add_component(entity.Translator, TILE_SIZE, 5)

    def update(self, dt):
        transl = self.components['translator']
        if transl.has_dest:
            transl.move(dt)
            
        return transl.has_dest

    def get_screen_pos(self, offset_x, offset_y):
        return self.components['translator'].get_pos_offset(offset_x, offset_y)

    def render(self, dest_surf, (x, y)):
        image = pygame.transform.flip(self.image, self.flip, False)
        dest_surf.blit(image, (x, y))
        

class Player(Entity):
    def __init__(self, x, y, name, image, blocks=False):
        Entity.__init__(self, x, y, name, image, blocks)
        self.actions = {game.UP: False, game.DOWN: False, game.LEFT: False, game.RIGHT: False}
        self.add_component(Fighter, 36, 10, 8)

    def move(self, dx, dy):
        if entity.Object.move(self, dx, dy):
            libtcod.map_compute_fov(self.map['fov_map'], self.x, self.y, LIGHT_RADIUS,
                                    FOV_LIGHT_WALLS, FOV_ALGO)

    def take_turn(self):
        dx = dy = 0
        actions = self.actions
        if actions[game.UP]: dy = -1
        elif actions[game.DOWN]: dy = +1
        elif actions[game.LEFT]: dx = -1; 
        elif actions[game.RIGHT]: dx = +1;
        if dx or dy:
            if dx < 0: self.flip = False
            else: self.flip = True
            
            target = None
            for object in self.map['objects']:
                if object != self and object.x == self.x+dx and object.y == self.y+dy:
                    target = object
                    break
            if target:
                # print 'The ' + target.name + ' laughs at your puny efforts to attack him!'
                self.components['fighter'].attack(target)
            else:
                self.move(dx, dy)
                self.components['translator'].set_destination(self.x, self.y)

class Monster(Entity):
    def __init__(self, x, y, name, image, blocks=False):
        Entity.__init__(self, x, y, name, image, blocks)
        self.add_component(Fighter, 8, 6, 12)
        self.add_component(MonsterAI, player)

    def take_turn(self):
        self.components['monster'].take_turn()

# CAMERA & RENDERER

class Camera:
    def __init__(self, followee, scr_w, scr_h, world_w, world_h):
        self.x = 0
        self.y = 0
        self.followee = followee
        self.translator = self.followee.components['translator']
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

    def __init__(self, camera):
        self.camera = camera

    def render_tiles(self, map):
        cam = self.camera
        data = map['data']
        fov_map = map['fov_map']
        for x in range(max(0, cam.x-1), min(cam.x + SCREEN_WIDTH + 1, MAP_WIDTH)):
            for y in range(max(0, cam.y-1), min(cam.y + SCREEN_HEIGHT + 1, MAP_HEIGHT)):
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
                screen_buffer.blit(img, (x * TILE_SIZE - cam.world_x, y * TILE_SIZE - cam.world_y), rect)

    def render_objects(self, map):
        cam = self.camera
        fov_map = map['fov_map']        
        for object in map['objects']:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                object.render(screen_buffer, object.get_screen_pos(cam.world_x, cam.world_y))

    def render(self, map):
        screen_buffer.fill(self.BLACK)
        self.render_tiles(map)
        self.render_objects(map)
        rect = screen.get_rect()
        text.set_text('HP: ' + str(player.components['fighter'].hp) + '/' +\
                      str(player.components['fighter'].max_hp))
        scr = pygame.transform.scale(screen_buffer, (rect.width, rect.height))
        screen.blit(scr, screen.get_rect())
        gui.render_gui(screen)
        pygame.display.flip()

# INITIALIZATION & MAIN LOOP

# generate map
map  = rl.map.make_map(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

# generate player
img = img_animes.subsurface((0*TILE_SIZE, 9*TILE_SIZE, TILE_SIZE, TILE_SIZE))
player = rl.map.place_object(map, 0, Player, "player", True, img)
libtcod.map_compute_fov(map['fov_map'], player.x, player.y, LIGHT_RADIUS,
                        FOV_LIGHT_WALLS, FOV_ALGO)

# generate other entities
img = img_animes.subsurface((0*TILE_SIZE, 12*TILE_SIZE, TILE_SIZE, TILE_SIZE))
rl.map.place_objects(map, 0, Monster, 2, 4, "monster", True, img)

# Gui

ts = TILE_SIZE * SCALE
p_w = SCREEN_WIDTH * ts
p_h = ts
p_rect = pygame.Rect((0, 0), (p_w, p_h))
p_col_fill = (64, 64, 196, 127)
p_col_stroke = (128, 128, 196, 127)

panel = gui.Panel(32, 32, rect=p_rect, fill=p_col_fill, stroke=p_col_stroke, stroke_size=3)
text = gui.Text(0, 0, parent=panel, padding=4, text="Text", color=(162, 162, 162), size=32)

# Camera & renderer

camera = Camera(player, SCREEN_WIDTH * TILE_SIZE, SCREEN_HEIGHT * TILE_SIZE,
                MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
renderer = Renderer(camera)

while 1:        
    game.update(map, player)
    
    # render the screen
    camera.update()
    renderer.render(map)

