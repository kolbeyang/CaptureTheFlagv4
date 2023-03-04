import pygame
import ctfv4_classes
import sys
import json
from pygame.locals import *

MENU = 0
PLAY = 1
GAMEOVER = 2
GAMESTATE = MENU

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (220,60,60)
BLUE = (44, 147, 226)
GREEN = (101,206,32)
ORANGE = (235,161,31)
YELLOW = (229,212,26)
MIDCOLOR = (15,60,83)
DARKCOLOR = (8, 38, 59)

fps = 24

font_reg = "SourceSansPro-Regular.otf"
font_bold = "SourceSansPro-Bold.otf"
fontsize = 80

delay = 4

screenwidth = 1200
screenheight = 600
pygame.init()
SCREEN = pygame.display.set_mode((screenwidth,screenheight))
#overlayer
OVERSCREEN = pygame.Surface((screenwidth,screenheight))
pygame.display.set_caption("Capture the Flag")
OVERSCREEN.set_colorkey(GREEN)

screenx = SCREEN.get_width()/2
screeny = SCREEN.get_height()/2

def read_json(file_name):
  data = json.load(open(file_name))
  return(data)

#import all images
menu_layout = pygame.image.load("ctfv4_menu_layout.jpg")
menu_layout_back = pygame.image.load("ctfv4_menu_layout_bottom.jpg")
score_screen = pygame.image.load("ctfv4_score_screen.jpg")
images = {}
images["menu"] = menu_layout
images["menu back"] = menu_layout_back
images["score screen"] = score_screen

#import all the maps
gamesettings = {}
maps = read_json("maps.json")
map_list = []
#get list of keys
for i in maps.keys():
    map_list.append(i)
map_index = 0
gamesettings["chosen_map"] = maps[map_list[map_index]]
gamesettings["0play"] = True
gamesettings["1play"] = True
gamesettings["2play"] = False
gamesettings["3play"] = False
gamesettings["winnum"] = 10

#button rects based on imported image
clicked = False #for use in buttons
clicked2 = False
buttons = {}
buttons["play"] = ctfv4_classes.Button(pygame.Rect((900, 405), (240,120)))
buttons["player0"] = ctfv4_classes.Button(pygame.Rect((495,60),(390,105)))
buttons["player1"] = ctfv4_classes.Button(pygame.Rect((495, 180),(390,105)))
buttons["player2"] = ctfv4_classes.Button(pygame.Rect((495, 300),(390,105)))
buttons["player3"] = ctfv4_classes.Button(pygame.Rect((495, 420),(390,105)))
buttons["winnum+"] = ctfv4_classes.Button(pygame.Rect((900,60),(240, 106)))
buttons["winnum-"] = ctfv4_classes.Button(pygame.Rect((900,285),(240, 106)))
buttons["score screen play"] = ctfv4_classes.Button(pygame.Rect((480,495),(240,75)))

#make chosen_map based on map_index
def update_map(num):
    global map_index, map_list, maps
    map_index = (map_index + num) % len(map_list)
    gamesettings["chosen_map"] = maps[map_list[map_index]]

#set all variables to their starting values, starts game
def reset(gamesettings):
    ctfv4_classes.init(SCREEN, fps)

    global Player, playergroup, wallgroup, flaggroup, speedbumpgroup, scores

    ctfv4_classes.wall_init(gamesettings)

    #class set-up
    Player = ctfv4_classes.Player
    playergroup = ctfv4_classes.get_groups()[0]
    wallgroup = ctfv4_classes.get_groups()[1]
    flaggroup = ctfv4_classes.get_groups()[2]
    scores = ctfv4_classes.get_score()


#used to prepare end screen
def endgame(color):
    global GAMESTATE
    GAMESTATE = GAMEOVER
    global wincolor, wintext, gamestats
    gamestats = ctfv4_classes.get_stats()
    wincolor = color

reset(gamesettings)

clock = pygame.time.Clock()
while True:
    mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            click = True
        else:
            click = False

    keystate = pygame.key.get_pressed()

    if GAMESTATE == MENU:
        SCREEN.blit(images["menu back"], (0,0))
        OVERSCREEN.blit(images["menu"], (0,0))

        #check for button clicks
        for key in buttons:
            button = buttons[key]

            #if the mouse is clicked and the mouse is in the right function

            #if function is in play
            if button.update(mouse, click):
                if key == "play" and (True in [gamesettings["0play"],gamesettings["0play"],gamesettings["0play"],gamesettings["0play"]]):
                    reset(gamesettings)
                    GAMESTATE = PLAY
                if key[:6] == "player":
                    #kept as string
                    number = key[-1]
                    #whether this player is playing
                    gamesettings[number + "play"] = not gamesettings[number + "play"]
                if key == "winnum+":
                    gamesettings["winnum"] += 1
                if key == "winnum-" and gamesettings["winnum"] >= 2:
                    gamesettings["winnum"] += -1

        #draw rects "holes" showing layer under marking whether a player is playing
        for i in range(4):
            if gamesettings[str(i) + "play"]:
                pygame.draw.rect(OVERSCREEN, GREEN, ((495, 60 + 120*i), (390, 105)))


        SCREEN.blit(OVERSCREEN, (0,0))

        #update side carousel
        for i in range(7):
            y = screenheight/8 * (i + 0.5)

            if i == 3:
                #blit main map option
                font = pygame.font.Font(font_bold,50)
                text = font.render(map_list[map_index], 1, BLUE)
                textpos = (screenwidth/40,y)
                SCREEN.blit(text, textpos)
            else:
                #peripheral options
                font = pygame.font.Font(font_reg,40)
                text = font.render(map_list[(map_index + i - 3)%len(map_list)], 1,

                                   MIDCOLOR)
                textpos = (screenwidth/40,y)
                SCREEN.blit(text, textpos)

            #keystates for moving options
            movecontroly = 0
            #look for up and down
            if keystate[K_DOWN] + keystate[K_UP] != 0:
                global clicked_value
                clicked = True
                clicked_value = keystate[K_DOWN] - keystate[K_UP]
            else:
                try:
                    if clicked == True and keystate[K_DOWN] + keystate[K_UP] == 0:
                        movecontroly = clicked_value
                except:
                    pass
                clicked = False

            #move up or down in options
            update_map(movecontroly)

        #blit winnum
        font = pygame.font.Font(font_bold, 80)
        text = font.render(str(gamesettings["winnum"]), 1, BLUE)
        center_to = (1020,225)
        textpos = (center_to[0] - text.get_width()/2, center_to[1] - text.get_height()/2)
        SCREEN.blit(text, textpos)

    if GAMESTATE == PLAY:
        movecontroly = [keystate[K_s] - keystate[K_w], keystate[K_DOWN] - keystate[K_UP], keystate[K_g] - keystate[K_t], keystate[K_k] - keystate[K_i]]
        movecontrolx = [keystate[K_d] - keystate[K_a], keystate[K_RIGHT] - keystate[K_LEFT], keystate[K_h] - keystate[K_f], keystate[K_l] - keystate[K_j]]

        #do all drawing
        SCREEN.fill(MIDCOLOR)
        for player in playergroup:
            movex = movecontrolx[player.num]
            movey = movecontroly[player.num]
            player.update([movex,movey])

        #draw the line down the center
        pygame.draw.line(SCREEN, DARKCOLOR, (screenx,0), (screenx,screenheight))

        wallgroup.update()
        flaggroup.update()

        #update scores and look for winner
        for color in ctfv4_classes.get_stats()["scores"]:
            scores[color].update()
            if scores[color].num >= gamesettings["winnum"]:
                endgame(color)

    if GAMESTATE == GAMEOVER:
        SCREEN.blit(images["score screen"], (0,0))

        positions = {RED:(60,60), BLUE:(1140,60)}
        #write the scores in the corners
        for color in ctfv4_classes.get_stats()["scores"]:
            score = ctfv4_classes.get_stats()["scores"][color]
            font = pygame.font.Font(font_bold, 80)
            text = font.render(str(score), 1, color)
            textpos = (positions[color][0] - text.get_width()/2, positions[color][1] - text.get_height()/2)
            SCREEN.blit(text, textpos)

        #prepare stat grid
        stat_grid = []
        #each list in this list is all one player's stats

        stat_list = ["tags", "resets", "steals", "scores"]
        for player in gamestats["playerstats"]:
            if player == 0: #player is not in play
                stat_grid.append(0)
            else:
                #player is in play
                individual_stat_list = []
                for i in stat_list:
                    indiv_stat = player[i]
                    individual_stat_list.append(indiv_stat)
                stat_grid.append(individual_stat_list)

        #blit the grid onto the SCREEN
        for row in range(4):
            for column in range(4):
                if stat_grid[column] != 0:
                    stat = stat_grid[column][row]
                    font = pygame.font.Font(font_bold, 60)
                    text = font.render(str(stat), 1, BLUE)
                    centerx = 420 + 120*column
                    centery = 165 + 90*row
                    textpos = (centerx - text.get_width()/2, centery - text.get_height()/2)
                    SCREEN.blit(text, textpos)


        if buttons["score screen play"].update(mouse,click):
            GAMESTATE = MENU


    clock.tick(fps)
    pygame.display.update()
