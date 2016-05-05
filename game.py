from __future__ import division
import pygame
from rl import kbd
from settings import *

clock = pygame.time.Clock()

GS_EXIT = 0
GS_IDLE = 1
GS_UPDATE = 2
PA_IDLE = 0
PA_TURN = 1

EXIT = 0
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

game_state = GS_IDLE
player_action = PA_IDLE
turn_count = 0

kbd.bind_key(pygame.K_UP, UP); kbd.bind_key(pygame.K_w, UP)
kbd.bind_key(pygame.K_DOWN, DOWN); kbd.bind_key(pygame.K_s, DOWN)
kbd.bind_key(pygame.K_LEFT, LEFT); kbd.bind_key(pygame.K_a, LEFT)
kbd.bind_key(pygame.K_RIGHT, RIGHT); kbd.bind_key(pygame.K_d, RIGHT)
kbd.bind_key(pygame.K_ESCAPE, EXIT)

def handle_keys(player):
    global wait
    global game_state
    global player_action

    kbd.handle_keys()

    for event in kbd.get():
        if event.type == kbd.KEYDOWN:
            if event.action == EXIT:
                game_state = GS_EXIT
            elif event.action in player.actions:
                player.actions[event.action] = True
        elif event.type == kbd.KEYUP:
            player.actions[event.action] = False

wait = 0
def update(player, object_group):
    global turn_count
    global game_state
    global player_action
    global wait
    
    handle_keys(player)

    if game_state == GS_IDLE and True in player.actions.values():
        game_state = GS_UPDATE 
        wait = TURN_SPEED
        turn_count += 1
        for object in object_group:
            object.take_turn()

    dt = clock.tick()
    if game_state == GS_UPDATE:
        wait -= dt
        object_group.update(dt/1000)
        if not next((x for x in object_group if x.is_updating == True), None):
            if True in player.actions.values():
                if wait <=0:
                    game_state = GS_IDLE
                    for object in object_group:
                        if object.dead: object.kill()

    if game_state == GS_EXIT:
        pygame.quit()

