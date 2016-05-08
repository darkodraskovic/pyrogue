class Camera:
    def __init__(self, followee, scr_w, scr_h, world_w, world_h):
        self.followee = followee
        self.x = self.followee.x
        self.y = self.followee.y
        self.scr_w = scr_w
        self.scr_h = scr_h
        self.world_w = world_w
        self.world_h = world_h

    def update(self):
        self.x = self.followee.x - self.scr_w/2
        self.y = self.followee.y - self.scr_h/2
        self.x = max(0, min(self.x, self.world_w - self.scr_w))
        self.y = max(0, min(self.y, self.world_h - self.scr_h))
