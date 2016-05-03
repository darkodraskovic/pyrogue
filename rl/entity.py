from __future__ import division
import math
import rl

class Component:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name
        owner.components[name] = self

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by an image on screen.
    def __init__(self, x, y, name, image, blocks=False, tile_size=24, tile_speed=5):
        self.x = x
        self.y = y
        self.name = name
        self.blocks = blocks
        self.image = image
        self.flip = False
        self.components = {}
        self.tile_size = tile_size
        self.tile_speed = tile_speed
        self.world_x = self.x * tile_size
        self.world_y = self.y * tile_size
        self.world_target_x = None
        self.world_target_y = None

    def add_component(self, component, *args):
        component(self, *args)

    def world_move(self, dt):
        dx = self.world_target_x - self.world_x
        dy = self.world_target_y - self.world_y
        dist = math.sqrt(dx**2 + dy**2)

        speed = self.tile_size * self.tile_speed * dt
        velX = (dx / dist) * speed;
        velY = (dy / dist) * speed;

        if dist > 1:
            self.world_x += velX;
            self.world_y += velY;
        else:
            self.world_x = self.world_target_x
            self.world_y = self.world_target_y
            self.world_target_x = None
            self.world_target_y = None
            return True

    def remove_component(self, component):
        if component.name not in self.components:
            return
        else:
            del self.components[component.name]

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
            # map movement
            self.x += dx
            self.y += dy
            # world movement
            self.world_target_x = self.x * self.tile_size
            self.world_target_y = self.y * self.tile_size
            return True
