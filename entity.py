import tcod as libtcod
from rl import entity
from rl import sprite
from settings import Settings
import game
import pygame


# COMPONENTS
class Fighter(entity.Component):
    # combat-related properties and methods (monster, player, NPC).
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
        damage = self.attack_pow - target.components["fighter"].defense_pow

        attack_str = self.owner.name.capitalize() + " attacks " + target.name
        if damage > 0:
            print(attack_str + " for " + str(damage) + " hit points.")
            target.components["fighter"].take_damage(damage)
        else:
            print(attack_str + " but it has no effects.")


class MonsterAI(entity.Component):
    # AI for a basic monster.
    def __init__(self, owner, target):
        entity.Component.__init__(self, owner, "monster")
        self.target = target

    def take_turn(self):
        target = self.target
        if not target:
            return
        monster = self.owner
        if libtcod.map_is_in_fov(monster.map["fov_map"], monster.map_x, monster.map_y):
            if monster.distance_to(target.map_x, target.map_y) >= 2:
                monster.move_towards(target.map_x, target.map_y)
                self.owner.components["translator"].set_destination(
                    self.owner.map_x, self.owner.map_y
                )
            else:
                self.owner.components["fighter"].attack(target)


# ENTITIES
class Entity(entity.Entity, sprite.AnimatedSprite):
    def __init__(self, x, y, name, anim_sheet, default_frame=0, blocks=False):
        entity.Entity.__init__(self, x, y, name, blocks)
        sprite.AnimatedSprite.__init__(
            self,
            x * Settings.TILE_SIZE,
            y * Settings.TILE_SIZE,
            anim_sheet,
            default_frame,
        )

        self.add_component(
            entity.Translator, Settings.TILE_SIZE, 1000 / Settings.TURN_SPEED
        )
        self.is_busy = False

        self.map = None
        self.dead = False

    def update(self, dt, viewport_x, viewport_y):
        # visuals
        if libtcod.map_is_in_fov(self.map["fov_map"], self.map_x, self.map_y):
            self.visible = 1
            self.update_rect(viewport_x, viewport_y)
            self.update_anim(dt)
        else:
            self.visible = 0

        # busy
        if self.is_busy:
            transl = self.components["translator"]
            if transl.has_dest:
                transl.move(dt)
            else:
                self.is_busy = False

    def take_turn(self):
        self.is_busy = True

    def compute_fov(self):
        libtcod.map_compute_fov(
            self.map["fov_map"],
            self.map_x,
            self.map_y,
            Settings.LIGHT_RADIUS,
            Settings.FOV_LIGHT_WALLS,
            Settings.FOV_ALGO,
        )

    def kill(self):
        if self.map:
            self.map["objects"].remove(self)
            del self.map
        pygame.sprite.DirtySprite.kill(self)


class Player(Entity):
    def __init__(self, x, y, name, anim_sheet, default_frame=0, blocks=False):
        Entity.__init__(self, x, y, name, anim_sheet, default_frame, blocks)
        self.actions = {
            game.UP: False,
            game.DOWN: False,
            game.LEFT: False,
            game.RIGHT: False,
        }
        self.add_component(Fighter, 36, 10, 8)

    def take_turn(self):
        Entity.take_turn(self)
        dx = dy = 0
        actions = self.actions
        if actions[game.UP]:
            dy = -1
        elif actions[game.DOWN]:
            dy = +1
        elif actions[game.LEFT]:
            dx = -1
        elif actions[game.RIGHT]:
            dx = +1
        if dx or dy:
            target = None
            for object in self.map["objects"]:
                if (
                    object != self
                    and object.map_x == self.map_x + dx
                    and object.map_y == self.map_y + dy
                ):
                    target = object
                    break
            if target:
                # print 'The ' + target.name + ' laughs at your puny efforts
                # to attack him!'
                self.components["fighter"].attack(target)
            else:
                self.move(dx, dy)
                self.compute_fov()
                self.components["translator"].set_destination(self.map_x, self.map_y)


class Monster(Entity):
    def __init__(
        self, x, y, name, anim_sheet, default_frame=0, blocks=False, target=None
    ):
        Entity.__init__(self, x, y, name, anim_sheet, default_frame, blocks)
        self.add_component(Fighter, 8, 6, 12)
        self.add_component(MonsterAI, target)

    def take_turn(self):
        Entity.take_turn(self)
        self.components["monster"].take_turn()
