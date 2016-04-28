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
    def __init__(self, x, y, name, image, blocks=False):
        self.x = x
        self.y = y
        self.name = name
        self.blocks = blocks
        self.image = image
        self.flip = False
        self.components = {}

    def add_component(self, component, *args):
        component(self, *args)

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
            self.x += dx
            self.y += dy
            return True
