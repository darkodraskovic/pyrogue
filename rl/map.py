import libtcodpy as libtcod

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


def create_room(data, room):
    # go through the tiles in the rectangle and make them passable
    # leave some walls at the border of the room
    # Python's range function excludes the last element in the loop
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            data[x][y].blocked = False
            data[x][y].block_sight = False


def create_h_tunnel(data, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        data[x][y].blocked = False
        data[x][y].block_sight = False


def create_v_tunnel(data, y1, y2, x):
    # vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        data[x][y].blocked = False
        data[x][y].block_sight = False

def compute_fov(data):
    map_width = len(data)
    map_height = len(data[0])
    fov_map = libtcod.map_new(map_width, map_height)
    for y in range(map_height):
        for x in range(map_width):
            libtcod.map_set_properties(fov_map, x, y,
                                       not data[x][y].block_sight, not data[x][y].blocked)
    return fov_map

def make_map(map_width, map_height, max_rooms, room_min_size, room_max_size):
    # fill map with "blocked" tiles
    data = [[Tile(True)
            for y in range(map_height)]
           for x in range(map_width)]

    rooms = []
    num_rooms = 0

    for r in range(max_rooms):
        # random width and height
        w = libtcod.random_get_int(0, room_min_size, room_max_size)
        h = libtcod.random_get_int(0, room_min_size, room_max_size)
        # random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, map_width - w - 1)
        y = libtcod.random_get_int(0, 0, map_height - h - 1)

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
            create_room(data, new_room)

            # center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms > 0:
                # all rooms after the first:
                # connect it to the previous room with a tunnel

                # center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(data, prev_x, new_x, prev_y)
                    create_v_tunnel(data, prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(data, prev_y, new_y, prev_x)
                    create_h_tunnel(data, prev_x, new_x, new_y)

            # finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    return {'data': data, 'fov_map': compute_fov(data), 'rooms': rooms, 'objects': []}

def is_blocked(map, x, y):
    data = map['data']    
    if data[x][y].blocked:
        return True

    for object in map['objects']:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def place_object(map, room_index, object_type, *args):
    room = map['rooms'][room_index]
    x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
    y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
    if not is_blocked(map, x, y):
        obj = object_type(x, y, *args)
        obj.map = map
        map['objects'].append(obj)
        return obj
    
def place_objects(map, room_index, object_type, min_objects, max_objects, *args):
    num_objects = libtcod.random_get_int(0, min_objects, max_objects)
    
    room = map['rooms'][room_index]
    objs = []
    for i in range(num_objects):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(map, x, y):
            obj = object_type(x, y, *args)
            obj.map = map
            map['objects'].append(obj)
            objs.append(obj)
    return objs
