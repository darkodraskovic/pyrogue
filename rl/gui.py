import pygame

# ITEM

items = []

class Item(pygame.sprite.DirtySprite):
    def __init__(self, x, y, parent, padding):
        pygame.sprite.DirtySprite.__init__(self)
        
        self.children = []
        if parent:
            parent.children.append(self)
            self.parent = parent
        else:
            items.append(self)
            self.parent = None

        self.visible = 1
        self.dirty = 2
        self.rect = self.image.get_rect()
        
        self.x = x
        self.y = y
        self.padding = padding
        self.update_rect()


    def update_rect(self):
        rect = self.rect
        rect.x = self.x + self.padding
        rect.y = self.y + self.padding
        
        parent = self.parent
        if parent == None: return

        while parent != None:
            rect.x += parent.x + parent.padding
            rect.y += parent.y + parent.padding
            parent = parent.parent

# PANEL

default_fill = (127, 127, 127, 255)
default_stroke = (255, 255, 255, 255)
default_rect = pygame.Rect((0,0), (64,32))

class Panel(Item):
    def __init__(self, x=0, y=0, parent=None, padding=0,
                 rect=default_rect, fill=default_fill, stroke=default_stroke, stroke_size=0):
        self.image = pygame.Surface(rect.size).convert_alpha()
        self.fill = fill
        self.stroke = stroke
        self.stroke_size = stroke_size
        pygame.draw.rect(self.image, fill, rect)
        if (stroke_size > 0):
            pygame.draw.rect(self.image, stroke, rect, stroke_size)
            
        Item.__init__(self, x, y, parent, padding)

# TEXT

class Text(Item):
    def __init__(self, x=0, y=0, parent=None, padding=0,
                 text="", font=None, size=16, color=default_fill, antialias=True):
        self.font = pygame.font.Font(font, size)
        self.text = text
        self.antialias = antialias
        self.color = color
        self.image = self.font.render(text, antialias, color)
        
        Item.__init__(self, x, y, parent, padding)
        
    def get_size(self):
        return self.font.get_size()

    def set_text(self, text):
        self.image = self.font.render(text, self.antialias, self.color)
