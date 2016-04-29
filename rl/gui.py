import pygame

default_fill = (127, 127, 127, 255)
default_stroke = (255, 255, 255, 255)
default_rect = pygame.Rect((0,0), (64,32))

panels = []
class Panel():
    def __init__(self, rect=default_rect, fill=default_fill, stroke=default_stroke, stroke_w=0):
        surf = self.surface = pygame.Surface(rect.size).convert_alpha()
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_w
        pygame.draw.rect(surf, fill, rect)
        if (stroke_w > 0):
            pygame.draw.rect(surf, stroke, rect, stroke_w)

    def get_rect(self):
        return self.surface.get_rect()

    def blit(self, dest):
        dest.blit(self.surface, self.get_rect().topleft)

def render_gui(dest):
    for panel in panels:
        panel.blit(dest)

def add_panel(panel):
    panels.append(panel)
