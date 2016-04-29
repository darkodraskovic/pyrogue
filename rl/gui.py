import pygame

# ITEM

items = []

class Item():
    def __init__(self):
        self.visible = True
        items.append(self)

# PANEL

default_fill = (127, 127, 127, 255)
default_stroke = (255, 255, 255, 255)
default_rect = pygame.Rect((0,0), (64,32))

class Panel(Item):
    def __init__(self, rect=default_rect, fill=default_fill, stroke=default_stroke, stroke_w=0):
        Item.__init__(self)
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

# RENDER

def render_gui(dest):
    for item in items:
        if item.visible:
            item.blit(dest)
