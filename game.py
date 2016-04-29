import pygame
from rl import kbd

clock = pygame.time.Clock()
wait = 0

GS_IDLE = 0
GS_BUSY = 1
GS_EXIT = 2
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

    if not kbd.is_pressed_any():
        game_state = GS_IDLE
    else:
        for event in kbd.get():
            if event.type == kbd.KEYDOWN:
                if event.action == EXIT:
                    game_state = GS_EXIT
                else:
                    player.actions[event.action] = True
                    player_action = PA_TURN
                    game_state = GS_BUSY
                    wait = 250
            elif event.type == kbd.KEYUP:
                player.actions[event.action] = False

    if game_state == GS_BUSY:
        if wait <= 0:
            player_action = PA_TURN
            wait = 100

def update(map, player):
    global wait
    global turn_count
    global game_state
    global player_action
    
    handle_keys(map, player)

    if player_action == PA_TURN:
        for object in map['objects']:
            object.update()
        player_action = PA_IDLE
        turn_count += 1
        
    if game_state == GS_EXIT:
        pygame.quit()

    wait -= clock.tick()
