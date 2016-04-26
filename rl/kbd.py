import pygame

KEYDOWN = pygame.USEREVENT
KEYUP = pygame.USEREVENT+1

actions = {}
pressed = {}

def bind_key(key, action):
    actions[key] = action
    pressed[action] = False

def set_pressed(key, value):
    pressed[actions[key]] = value

def is_pressed(action):
    return pressed[action]

def is_pressed_any():
    return True in pressed.values()

def handle_keys():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in actions:
                set_pressed(event.key, True)
                pygame.event.post(pygame.event.Event(KEYDOWN, {'action': actions[event.key]}))
        elif event.type == pygame.KEYUP:
            if event.key in actions:
                set_pressed(event.key, False)
                pygame.event.post(pygame.event.Event(KEYUP, {'action': actions[event.key]}))
