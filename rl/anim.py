# First create an Anim object which contains a list of frames and the type of play mode used. The frames are formatted as [(frame1, duration1), (frame2, duration2), ...] with the duration measured in seconds. The play mode can be either LOOP (which continuously loops) or ONCE (which plays once then stops).

# The AnimCursor keeps track of playback information. For example, each sprite should have its own AnimCursor to keep track of its own animation.

# AnimCursor.use_anim(anim) is used to select which animation the animation cursor should be playing.

# AnimCursor.play(playspeed = 1.0) starts playing the animation at the specified speed. A play speed of 1.0 plays the animation at normal speed, 0.5 will be at half speed, and 2.0 will be twice as fast.

# AnimCursor.pause() pauses the animation.

# AnimCursor.unpause() unpauses the animation.

# AnimCursor.update(dt) Updates the animation with td being the difference in time between updates measured in 1/1000s of a second.

# After updating the animation cursor will contain information about the current state of the animation.

# AnimCursor.current is the current frame information. If this is being used for sprite animation then this will contain the surface that the sprite should use.

# AnimCursor.next is the next frame that will be played after this one. If you intend to interpolate between the current and next frame (such as for following a path) then this can be used along with AnimCursor.transition, for example: x = cursor.current * (1.0 - cursor.transition) + cursor.next * cursor.transition.

# AnimCursor.played is a list of frames that had been played between updates. This can be used if you want to ensure that frames are not skipped, for example if you wanted to have some time-dependent events in a game.

# AnimCursor.playing tells if the animation is currently playing or is stopped.

# AnimCursor.playtime keeps track of how long the animation has been playing.

LOOP = 0
ONCE = 1

class Anim:
    def __init__(self, frames, mode=LOOP):
        self.frames = frames
        self.playmode = mode
        

class AnimCursor:
    def __init__(self):
        self.anim = None
        self.frame_num = 0
        self.current = None
        self.next = None
        self.played = []
        self.transition = 0.0
        self.playing = True
        self.playtime = 0.0

        self.frame_time = 0.0
        self.timeleft = 0.0
        self.playspeed = 1.0

    def use_anim(self, anim):
        self.anim = anim
        self.reset()

    def reset(self):
        self.current = self.anim.frames[0][0]
        self.timeleft = self.anim.frames[0][1]
        self.frame_time = self.timeleft
        self.next_frame = (self.frame_num + 1) % len(self.anim.frames)
        self.next = self.anim.frames[self.next_frame][0]
        self.frame_num = 0
        self.playtime = 0.0
        self.transition = 0.0

    def play(self, playspeed=1.0):
        self.playspeed = playspeed
        self.reset()
        self.unpause()

    def pause(self):
        self.playing = False

    def unpause(self):
        self.playing = True

    def update(self, dt):
        dt = dt * self.playspeed
        self.played = []
        if self.playing:
            self.playtime += dt
            self.timeleft -= dt
            self.transition = self.timeleft / self.frame_time

            while self.timeleft <= 0.0:
                self.frame_num = (self.frame_num + 1) % len(self.anim.frames)
                if self.anim.playmode == ONCE and self.frame_num == 0:
                    self.pause()
                    return

                self.next_frame = (self.frame_num + 1) % len(self.anim.frames)
                
                frame,time = self.anim.frames[self.frame_num]
                self.frame_time = time
                self.timeleft += time
                self.current = frame
                self.next = self.anim.frames[self.next_frame][0]
                self.played.append(frame)
                self.transition = self.timeleft / time
                
                if self.frame_num == 0:
                    self.playtime = self.timeleft
