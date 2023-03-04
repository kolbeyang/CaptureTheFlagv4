import pygame
from pygame.locals import *

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (220,60,60)
BLUE = (44, 147, 226)
GREEN = (101,206,32)
ORANGE = (235,161,31)
YELLOW = (229,212,26)
MIDCOLOR = (15,60,83)
DARKCOLOR = (8, 38, 59)

DEFAULT_COUNTDOWN = 30
SPEED_MULTIPLIER = 1.5

def reset():
    global playergroup, playerlist, wallgroup, flaggroup, scores
    playergroup = pygame.sprite.Group()
    playerlist = [0,0,0,0]
    wallgroup = pygame.sprite.Group()
    flaggroup = pygame.sprite.Group()

    scores = {RED: Score(RED),BLUE: Score(BLUE)}

def init(screen, frames_per_second):
    global SCREEN, fps, screenx, screeny
    SCREEN = screen
    fps = frames_per_second

    screenx = SCREEN.get_width()/2
    screeny = SCREEN.get_height()/2

    reset()

def get_groups():
    return([playergroup,wallgroup,flaggroup])

def get_score():
    return(scores)

def get_stats():
    #returns game stats for score screen
    gamestats = {}
    gamestats["scores"] = {RED:scores[RED].num, BLUE: scores[BLUE].num}
    gamestats["playerstats"] = [0,0,0,0]
    for i in range(4):
        if playerlist[i] != 0:
            gamestats["playerstats"][i] = playerlist[i].gamestats
    return(gamestats)

class Player(pygame.sprite.Sprite):
    width = 40
    height = 40
    def __init__(self,color,num,x,y):
        super().__init__()

        #image variables ==========

        self.num = num

        self.image = pygame.Surface((self.width,self.height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.startpos = (x,y)
        self.color = color
        self.image.set_colorkey(WHITE)
        playergroup.add(self)
        playerlist[self.num] = self
        self.myside = True
        self.flag = 0
        #movement variables
        self.control = [0,0]
        self.startspeed = 9/(fps/36)
        self.speed = self.startspeed
        self.countdown = 0

        #gamestats
        self.gamestats = {}
        self.gamestats["steals"] = 0
        self.gamestats["scores"] = 0
        self.gamestats["tags"] = 0
        self.gamestats["resets"] = 0

    def draw(self):
        self.image.fill(self.color)
        SCREEN.blit(self.image,(self.rect.x,self.rect.y))

    def get_speed(self):
        if self.speed > self.startspeed :
            self.speed -= 1
        return self.speed

    def move(self):
        #differences in x and y values
        movex = 0
        movey = 0
        speed = self.get_speed()
        movex += self.control[0]*self.speed
        movey += self.control[1]*self.speed

        self.rect.x += movex
        for wall in wallgroup:
            if self.rect.colliderect(wall.rect):
                completed = False
                while completed == False:
                    self.rect.x += -movex/abs(movex)
                    if not self.rect.colliderect(wall.rect):
                        completed = True
        self.rect.y += movey
        for wall in wallgroup:
            if self.rect.colliderect(wall.rect):
                completed = False
                while completed == False:
                    self.rect.y += -movey/abs(movey)
                    if not self.rect.colliderect(wall.rect):
                        completed = True

    def flag_check(self):
        #check to see if I'm on a flag
        if self.flag == 0:
            for flag in flaggroup:
                if flag.color != self.color and self.rect.colliderect(flag.rect):
                    flag.capture(self)
                    self.flag = flag
                    #update the gamestats
                    self.gamestats["steals"] += 1
                if flag.color == self.color and self.rect.colliderect(flag.rect) and flag.captured == False:
                    self.rect.topleft = self.startpos
                    self.set_countdown()

    def get_tagged(self):
        if self.flag != 0:
            self.flag.captured = False
            self.flag = 0
        self.rect.topleft = self.startpos
        self.gamestats["resets"] += 1
        self.set_countdown()

    def add_tag(self):
        #when I tag someone else, called by opponent
        self.flag = 0
        self.gamestats["tags"] += 1

    def tag_check(self):
        for player in playergroup:
            if self.rect.colliderect(player.rect) and player.color != self.color and self.myside == False:
                player.add_tag()
                self.get_tagged()

    def add_score(self,num):
        scores[self.color].add(num)
        self.gamestats["scores"] += 1

    def update_myside(self):
        #update myside
        if self.color == RED:
            side = 0
        else:
            side = 1
        self.myside = (side*2 - 1)*(self.rect.x - screenx) > 0

    def set_countdown(self, duration = DEFAULT_COUNTDOWN):
        self.countdown = duration

    def update_countdown(self):
        if self.countdown > 0:
            self.countdown -= 1

    def set_speed_boost(self, previous_control, current_control):
        x1 = previous_control[0]
        y1 = previous_control[1]
        x2 = current_control[0]
        y2 = current_control[1]
        x_juke = x1*x2 == -1
        y_juke = y1*y2 == -1
        if x_juke != y_juke:
            self.speed = self.startspeed * int(SPEED_MULTIPLIER)

    def update(self, control):
        self.update_myside()
        self.set_speed_boost(self.control, control)
        self.control = control
        if self.countdown == 0:
            self.move()
        else:
            self.update_countdown()
        self.tag_check()
        self.flag_check()
        self.draw()

class Flag(pygame.sprite.Sprite):
    width = 20
    height = 20
    def __init__(self,color,x,y):
        super().__init__()
        self.color = color

        self.width = Flag.width
        self.height = Flag.height
        self.image = pygame.Surface((self.width,self.height))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.startpos = (x,y)

        self.captured = False
        self.captor = 0
        self.myside = True
        flaggroup.add(self)

    def draw(self):
        self.image.fill(self.color)
        SCREEN.blit(self.image,(self.rect.x,self.rect.y))

    def capture(self, captor):
        self.captor = captor
        self.captured = True

    #runs when self is captured
    def capture_check(self):
        #update myside
        if self.startpos[0] < screenx:
            side = 0
        else:
            side = 1
        self.myside = (side*2 - 1)*(self.rect.centerx - screenx) > 0

        self.rect.center = self.captor.rect.center
        if self.myside == False:
            self.captured = False
            self.captor.add_score(1)
            self.captor.flag = 0
            self.rect.topleft = self.startpos

    def update(self):
        if self.captured == True:
            self.capture_check()
        else:
            self.rect.topleft = self.startpos
        self.draw()

class Wall(pygame.sprite.Sprite):
    def __init__(self,rect,color):
        super().__init__()

        self.rect = rect
        self.image = pygame.Surface((self.rect.width,self.rect.height))
        self.image.get_rect().x = self.rect.x
        self.image.get_rect().y = self.rect.y
        self.color = color
        self.image.set_colorkey(WHITE)

        wallgroup.add(self)
    def draw(self):
        self.image.fill(self.color)
        SCREEN.blit(self.image,(self.rect.x,self.rect.y))

    def update(self):
        self.draw()

class Button():
    def __init__(self, rect):
        self.rect = rect
        self.old_value = False

    def update(self,mousepos, mouseclick):
        condition = self.rect.collidepoint(mousepos) and mouseclick
        if self.old_value == False and condition:
            self.old_value = condition
            return(True)
        else:
            self.old_value = condition
            return(False)

class Score(pygame.sprite.Sprite):
    def __init__(self,color):
        super().__init__()
        self.color = color
        self.num = 0
        self.width = 80
        self.height = 80
        self.image = pygame.Surface((self.width,self.height))
        self.image.set_colorkey(WHITE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

    def set_pos(self,x,y):
        self.rect.topleft = (x,y)

    def add(self,num):
        self.num += num

    def draw(self):
        self.image.fill(WHITE)
        font = pygame.font.Font(None, 60)
        text = font.render(str(self.num), 0, self.color)
        textrect = text.get_rect()
        textpos = [self.rect.width/2 - textrect.width/2,self.rect.height/2 - textrect.height/2]
        self.image.blit(text, textpos)
        SCREEN.blit(self.image,(self.rect.x,self.rect.y))


    def update(self):
        self.draw()


def wall_init(settings):
    global gamesettings
    gamesettings = settings
    chosen_map = gamesettings["chosen_map"]["map"]
    start_row = gamesettings["chosen_map"]["startrow"]
    block_width = 40
    block_height = 40
    block_num_across = len(chosen_map[0])
    block_num_down = len(chosen_map)
    for i in range(block_num_down):
        row = chosen_map[i]
        #just to cut down on inefficiency regarding the walls updating
        if row == "wwwwwwwwwwwwwwwwwwwwwwwwwwwwww":
            rect = pygame.Rect(0,(i - start_row)*block_height,block_width*block_num_across,block_height)
            Wall(rect,DARKCOLOR)
        else:
            for num in range(block_num_across):
                character = row[num]
                x = num*block_width
                y = (i - start_row)*block_height
                if character == "w":
                    rect = pygame.Rect(x,y,block_width,block_height)
                    Wall(rect,DARKCOLOR)
                #for score
                if character == "R":
                    rect = pygame.Rect(x,y,block_width,block_height)
                    Wall(rect,DARKCOLOR)
                    scores[RED].set_pos(x,y)
                #for score
                if character == "B":
                    rect = pygame.Rect(x,y,block_width,block_height)
                    Wall(rect,DARKCOLOR)
                    scores[BLUE].set_pos(x,y)

                #players
                if character == "0" and gamesettings["0play"]:
                    Player(RED, 0, x, y)
                if character == "1" and gamesettings["1play"]:
                    Player(BLUE, 1, x, y)
                if character == "2" and gamesettings["2play"]:
                    Player(RED, 2, x, y)
                if character == "3" and gamesettings["3play"]:
                    Player(BLUE, 3, x, y)

                #red flag
                if character == "r":
                    flagwidth = Flag.width
                    flagheight = Flag.height
                    Flag(RED,x + (- flagwidth + block_width)/2,y + (- flagheight + block_height)/2)

                #blue flag
                if character == "b":
                    flagwidth = Flag.width
                    flagheight = Flag.height
                    Flag(BLUE,x + (- flagwidth + block_width)/2,y + (- flagheight + block_height)/2)

