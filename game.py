from __future__ import division
import pygame
from rl import kbd

clock = pygame.time.Clock()

GS_IDLE = 0
GS_BUSY = 1
GS_EXIT = 2
GS_TRANSLATE = 3
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

def handle_keys(map, player):
    global wait
    global game_state
    global player_action

    kbd.handle_keys()

    for event in kbd.get():
        if event.type == kbd.KEYDOWN:
            if event.action == EXIT:
                game_state = GS_EXIT
            elif game_state == GS_IDLE:
                player_action = PA_TURN
                game_state = GS_TRANSLATE
            player.actions[event.action] = True
        elif event.type == kbd.KEYUP:
            player.actions[event.action] = False

def update(map, player):
    global turn_count
    global game_state
    global player_action

    dt = clock.tick() / 1000

    handle_keys(map, player)

    if player_action == PA_TURN:
        for object in map['objects']:
            object.update()
        player_action = PA_IDLE
        turn_count += 1

    if game_state == GS_TRANSLATE:
        translating = False
        for object in map['objects']:
            if object.world_target_x:
                object.world_move(dt)
                translating = True
        if not translating:
            if kbd.is_pressed_any():
                player_action = PA_TURN
            else:
                game_state = GS_IDLE

    if game_state == GS_EXIT:
        pygame.quit()

