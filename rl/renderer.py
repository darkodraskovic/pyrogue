import pygame
import os

class Renderer:
    BLACK = (0,0,0)
    global screen_buffer

    def __init__(self, scr_w, scr_h, scale):
        self.screen = pygame.display.set_mode((scr_w * scale, scr_h * scale))
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        self.screen_buffer = pygame.Surface((scr_w, scr_h))
        
    def update(self, world_group, gui_group):
        screen = self.screen
        screen_buffer = self.screen_buffer
        screen_buffer.fill(self.BLACK)

        # world
        world_group.draw(screen_buffer)
        rect = screen.get_rect()
        scr = pygame.transform.scale(screen_buffer, (rect.width, rect.height))
        screen.blit(scr, screen.get_rect())

        # GUI
        gui_group.draw(screen)

        pygame.display.flip()
