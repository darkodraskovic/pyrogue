from rl import libtcodpy as libtcod
from rl import entity
from rl import anim
from settings import *
import pygame
import game


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
        if self.hp <= 0:
            self.owner.dead = True

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
        target = self.target
        if not target: return
        monster = self.owner
        if libtcod.map_is_in_fov(monster.map['fov_map'], monster.x, monster.y):
            if monster.distance_to(target.x, target.y) >= 2:
                monster.move_towards(target.x, target.y)
                self.owner.components['translator'].set_destination(self.owner.x, self.owner.y)
            else:
                self.owner.components['fighter'].attack(target)
            

# ENTITIES
class Entity(entity.Entity, anim.AnimatedSprite):
    def __init__(self, x, y, name, anim_sheet, default_frame=0, blocks=False):
        entity.Entity.__init__(self, x, y, name, blocks)
        anim.AnimatedSprite.__init__(self, anim_sheet, default_frame)

        self.add_component(entity.Translator, TILE_SIZE, 1000 / TURN_SPEED)
        self.is_updating = False

        self.map = None
        self.dead = False

    def update(self, dt):
        if self.is_updating:
            transl = self.components['translator']
            if transl.has_dest:
                transl.move(dt)
            else:
                self.is_updating = False

    def update_rect(self, offset_x=0, offset_y=0):
        transl = self.components['translator']
        self.rect.x = transl.x - offset_x
        self.rect.y = transl.y - offset_y

    def take_turn(self):
        self.is_updating = True

    def compute_fov(self):
        libtcod.map_compute_fov(self.map['fov_map'], self.x, self.y,
                                LIGHT_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    def kill(self):
        if self.map:
            self.map['objects'].remove(self)
            del self.map
        pygame.sprite.DirtySprite.kill(self)

class Player(Entity):
    def __init__(self, x, y, name, anim_sheet, default_frame=0, blocks=False):
        Entity.__init__(self, x, y, name, anim_sheet, default_frame, blocks)
        self.actions = {game.UP: False, game.DOWN: False, game.LEFT: False, game.RIGHT: False}
        self.add_component(Fighter, 36, 10, 8)

    def take_turn(self):
        Entity.take_turn(self)
        dx = dy = 0
        actions = self.actions
        if actions[game.UP]: dy = -1
        elif actions[game.DOWN]: dy = +1
        elif actions[game.LEFT]: dx = -1; 
        elif actions[game.RIGHT]: dx = +1;
        if dx or dy:
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
                self.compute_fov()
                self.components['translator'].set_destination(self.x, self.y)

class Monster(Entity):
    def __init__(self, x, y, name, anim_sheet, default_frame=0, blocks=False, target=None):
        Entity.__init__(self, x, y, name, anim_sheet, default_frame, blocks)
        self.add_component(Fighter, 8, 6, 12)
        self.add_component(MonsterAI, target)

    def take_turn(self):
        Entity.take_turn(self)
        self.components['monster'].take_turn()

