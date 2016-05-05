from __future__ import division
import math
import rl

# BASE CLASSES

class Component:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name
        owner.components[name] = self

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    def __init__(self, x, y, name, blocks=False):
        self.x = x
        self.y = y
        self.name = name
        self.blocks = blocks
        self.components = {}

    def add_component(self, component, *args):
        component(self, *args)

    def remove_component(self, component):
        if component.name not in self.components:
            return
        else:
            del self.components[component.name]

    def take_turn():
        pass
    
    def update():
        pass
    
    def distance_to(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx**2 + dy**2)

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        # if not map[self.x + dx][self.y + dy].blocked:
        if not rl.map.is_blocked(self.map, self.x+dx, self.y+dy):
            self.x += dx
            self.y += dy
            return True

# DERIVED CLASSES

class Translator(Component):
    def __init__(self, owner, tile_size, tile_speed):
        Component.__init__(self, owner, "translator")
        self.tile_size = tile_size
        self.tile_speed = tile_speed
        self.x = owner.x * tile_size
        self.y = owner.y * tile_size
        self.dest_x = None
        self.dest_y = None
        self.has_dest = False

    def move(self, dt):
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist > 1:
            speed = self.tile_size * self.tile_speed * dt
            velX = (dx / dist) * speed;
            velY = (dy / dist) * speed;
            self.x += velX;
            self.y += velY;
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.dest_x = None
            self.dest_y = None
            self.has_dest = False

    def set_destination(self, x, y):
        self.dest_x = x * self.tile_size
        self.dest_y = y * self.tile_size
        self.has_dest = True

    def get_pos(self):
        return (self.x, self.y)

    def get_pos_offset(self, offset_x, offset_y):
        return (self.x - offset_x, self.y - offset_y)

