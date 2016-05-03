import pygame

# ITEM

items = []

class Item():
    def __init__(self, x, y, parent, padding):
        self.visible = True
        self.x = x
        self.y = y
        self.padding = padding

        self.children = []
        if parent:
            parent.children.append(self)
            self.parent = parent
        else:
            items.append(self)
            self.parent = None

    def render(self, dest, transl_x, transl_y):
        if self.parent != None:
            transl_x += self.parent.x + self.padding
            transl_y += self.parent.y + self.padding
            
        dest.blit(self.surface, (
            transl_x + self.x,
            transl_y + self.y)
        )

        for child in self.children:
            child.render(dest, transl_x, transl_y)

# PANEL

default_fill = (127, 127, 127, 255)
default_stroke = (255, 255, 255, 255)
default_rect = pygame.Rect((0,0), (64,32))

class Panel(Item):
    def __init__(self, x=0, y=0, parent=None, padding=0,
                 rect=default_rect, fill=default_fill, stroke=default_stroke, stroke_size=0):
        Item.__init__(self, x, y, parent, padding)
        surf = self.surface = pygame.Surface(rect.size).convert_alpha()
        self.fill = fill
        self.stroke = stroke
        self.stroke_size = stroke_size
        pygame.draw.rect(surf, fill, rect)
        if (stroke_size > 0):
            pygame.draw.rect(surf, stroke, rect, stroke_size)

    def get_rect(self):
        return self.surface.get_rect()

# TEXT

class Text(Item):
    def __init__(self, x=0, y=0, parent=None, padding=0,
                 text="", font=None, size=16, color=default_fill, antialias=True):
        Item.__init__(self, x, y, parent, padding)
        self.font = pygame.font.Font(font, size)
        self.text = text
        self.antialias = antialias
        self.color = color
        self.surface = self.font.render(text, antialias, color)
        
    def get_size(self):
        return self.font.get_size()

    def set_text(self, text):
        self.surface = self.font.render(text, self.antialias, self.color)

# RENDERER

def render_gui(dest):
    for item in items:
        if item.visible: item.render(dest, 0, 0)
