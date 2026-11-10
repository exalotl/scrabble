"""
same as before except rack refresh fixed
"""

################# initialisation
import pygame
import copy
import random
from dawg import *

pygame.init()
screen = pygame.display.set_mode((720, 800))
clock = pygame.time.Clock()
running = True
pygame.display.set_caption("Scrabble")

font1 = pygame.font.Font("freesansbold.ttf", 20)
font2 = pygame.font.Font("freesansbold.ttf", 15)


################## classes
class Tile:
    def __init__(self, letter, spawnx, spawny):
        self.Letter = letter
        self.Surface = font1.render(letter, True, font_colour)
        self.Rect = self.Surface.get_rect()
        self.Rect.width = tile_size
        self.Rect.height = tile_size
        self.Rect.x = spawnx
        self.Rect.y = spawny

        if letter != "":
            self.ScoreSurface = font2.render(str(score[letter]), True, font_colour)

class TextSquare:
    def __init__(self, text, colour, spawnx, spawny):
        self.Text = text
        self.Surface = font1.render(text, True, colour) ### font colour change
        self.Rect = self.Surface.get_rect()
        self.Rect.width += 25
        self.Rect.height += 25
        self.Rect.x = spawnx - self.Rect.width//2
        self.Rect.y = spawny - self.Rect.height//2

#################### functions
def rendertextobject(ob, colour):
    centred_rect = ob.Surface.get_rect(center=ob.Rect.center)
    pygame.draw.rect(screen, colour, ob.Rect)
    screen.blit(ob.Surface, centred_rect)

def rendertile(tl, colour):
    centred_rect = tl.Surface.get_rect(center=tl.Rect.center)
    pygame.draw.rect(screen, colour, tl.Rect)
    screen.blit(tl.Surface, centred_rect)
    screen.blit(tl.ScoreSurface, (centred_rect.x + 15, centred_rect.y + 15) )

def drawgrid():

    for i in range(15):
        for j in range(15):

            """
            """

            cell = Tile(grid[i][j], gridx + tile_size*j, gridy+ tile_size*i)
            centred_rect = cell.Surface.get_rect(center=cell.Rect.center)
            if grid[i][j] != "":
                pygame.draw.rect(screen, (200, 200,100), cell.Rect)
            pygame.draw.rect(screen, "black", cell.Rect, 1)
            screen.blit(cell.Surface, centred_rect)

            #pygame.draw.rect(screen, (0, 0, 0), 
            #    [gridx + tile_size*j, gridy+ tile_size*i, tile_size, tile_size], 1)
    grid_size = 15*tile_size
    pygame.draw.rect(screen, (0, 0, 0), 
                 [gridx, gridy, grid_size, grid_size], 2)

def processgrid(): # return points or -1 if invalid
    horicounted = [[False for i in range(15)] for j in range(15)]
    verticounted = [[False for i in range(15)] for j in range(15)]
    words = []
    newpoints = 0
    for i in range(15):
        for j in range(15):
            # hori check
            if newgrid[i][j] != grid[i][j] and not horicounted[i][j]:
                if (j != 0 and newgrid[i][j-1] != "") or (j != 14 and newgrid[i][j+1] != ""): # avoid out of bounds error
                    k = j
                    while k > 0 and newgrid[i][k-1] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and newgrid[i][k] != "":
                        curword += newgrid[i][k]
                        horicounted[i][k] = True
                        newpoints += score[newgrid[i][k]]
                        k += 1
                    words.append(curword)
                    curword = ""
            # verti check
            if newgrid[i][j] != grid[i][j] and not verticounted[i][j]:
                if (i != 0 and newgrid[i-1][j] != "") or (i != 14 and newgrid[i+1][j] != ""): # avoid out of bounds error
                    k = i
                    while k > 0 and newgrid[k-1][j] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and newgrid[k][j] != "":
                        curword += newgrid[k][j]
                        verticounted[k][j] = True
                        newpoints += score[newgrid[k][j]]
                        k += 1
                    words.append(curword)
                    curword = ""

    if len(words) == 0:
        return -1

    for word in words:
        print(word, end= " , ")
    print()

    for word in words:
        if wordbank.search(word) == False:
            return -1
        
    return newpoints
            
def fillrack(player): # take in 0 or 1

    """
    for l in bag:
        print(l, end = " ")
    print()
    """
    
    while len(rack[player]) < 7 and len(bag) != 0:
        rack[player].append(bag.pop())

def refreshtiles():
    tiles[0] = []
    for i in range(len(rack[0])):
        tiles[0].append(Tile(rack[0][i], 50 * i, racky))

    tiles[1] = []
    for i in range(len(rack[1])):
        tiles[1].append(Tile(rack[1][i], screen.width - (50 * i) - 60, racky))

################## variables
tiles = [[], []] # p1, p2
dragging = -1

grid = [["" for i in range(15)] for j in range(15)]
#grid[5][5] = "A"

newgrid = copy.deepcopy(grid)

score = {"A":1, "B":3, "C":3, "D":2, "E":1, "F":4, 
         "G":2, "H":4, "I":1, "J":8, "K":5, "L":1,
         "M":3, "N":1, "O":1, "P":3, "Q":10, "R":1,
         "S":1, "T":1, "U":1, "V":4, "W":4, "X":8,
         "Y":4, "Z":10, "-":0}
bag = [
    "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", 
    "A", "A", "A", "A", "A", "A", "A", "A", "A", 
    "I", "I", "I", "I", "I", "I", "I", "I", "I", 
    "O", "O", "O", "O", "O", "O", "O", "O", 
    "N", "N", "N", "N", "N", "N", 
    "R", "R", "R", "R", "R", "R", 
    "T", "T", "T", "T", "T", "T", 
    "L", "L", "L", "L", 
    "S", "S", "S", "S", 
    "U", "U", "U", "U", 
    "D", "D", "D", "D", 
    "G", "G", "G", 
    "B", "B", "C", "C", "M", "M", "P", "P", 
    "F", "F", "H", "H", "V", "V", "W", "W", "Y", "Y", 
    "K", "J", "X", "Q", "Z"
] # blanks not included for now

random.shuffle(bag)

rack = [[], []]
fillrack(0)
fillrack(1)

tile_size = 40
font_colour = (0, 0, 0)
gridx = screen.width // 2 - (7.5*tile_size)
gridy = 100
leavingposx = 0
leavingposy = 0
racky = 750
bgcolour = "grey"
infoboxtext = ""
curplayer = 0 
playerpoints = [0, 0]


wordbank = DAWG()
wordbank.build("CSW24.txt")

################# main loop

refreshtiles()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(tiles[curplayer])):
                if tiles[curplayer][i].Rect.collidepoint(event.pos):
                    dragging = i
                    mouse_x, mouse_y = event.pos
                    offset_x = tiles[curplayer][i].Rect.x - mouse_x
                    offset_y = tiles[curplayer][i].Rect.y - mouse_y
                    leavingrow = round((tiles[curplayer][dragging].Rect.y - gridy) / tile_size)
                    leavingcol = round((tiles[curplayer][dragging].Rect.x - gridx) / tile_size)
            if submitbutton.Rect.collidepoint(event.pos):
                # submit button pressed
                res = processgrid()
                if res == -1:
                    infoboxtext = "Invalid move"
                else:
                    infoboxtext = "Valid move"
                    playerpoints[curplayer] += res
                    grid = copy.deepcopy(newgrid)
                    newrack = []
                    for i in range(len(tiles[curplayer])):
                        row = round((tiles[curplayer][i].Rect.y - gridy) / tile_size)
                        col = round((tiles[curplayer][i].Rect.x - gridx) / tile_size)

                        if (row < 0 or row >= 15) or (col < 0 or col >= 15):
                            newrack.append(tiles[curplayer][i].Letter)

                    rack[curplayer] = copy.deepcopy(newrack)
                    fillrack(curplayer)
                    refreshtiles()

                    if curplayer == 0:
                        tiles[curplayer][i].Rect.x = 50 * i
                    else:
                        tiles[curplayer][i].Rect.x = screen.width - (50 * i) - 60
                    tiles[curplayer][i].Rect.y = racky

                    curplayer = (curplayer+1)%2

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging != -1:
                row = round((tiles[curplayer][dragging].Rect.y - gridy) / tile_size)
                col = round((tiles[curplayer][dragging].Rect.x - gridx) / tile_size)
                #print(row, col)

                if (leavingrow >= 0 and leavingrow < 15) and (leavingcol >= 0 and leavingcol < 15):
                    newgrid[leavingrow][leavingcol] = ""
                if (row >= 0 and row < 15) and (col >= 0 and col < 15):
                    if (newgrid[row][col] == ""):
                        tiles[curplayer][dragging].Rect.x = col*tile_size + gridx
                        tiles[curplayer][dragging].Rect.y = row*tile_size + gridy
                        newgrid[row][col] = tiles[curplayer][dragging].Letter
                    else:
                        tiles[curplayer][dragging].Rect.y = racky


                
            dragging = -1
        elif event.type == pygame.MOUSEMOTION:
            if dragging != -1:
                mouse_x, mouse_y = event.pos
                tiles[curplayer][dragging].Rect.x = offset_x + mouse_x
                tiles[curplayer][dragging].Rect.y = offset_y + mouse_y
        elif event.type == pygame.KEYDOWN:
            """
            for i in range(15):
                for j in range(15):
                    print(newgrid[i][j], end=",")
                print("\n")
            """

            #print(processgrid()) # num points or -1 if invalid


    screen.fill(bgcolour)

    # RENDER HERE

    #render buttons / other
    submitbutton = TextSquare("Submit", "white", 600, 70)
    rendertextobject(submitbutton, (128, 58, 45))
    playerdisplay = TextSquare("Player " + str(curplayer+1) + " turn", font_colour, screen.width // 2, 20)
    rendertextobject(playerdisplay, bgcolour)
    infobox = TextSquare(infoboxtext, font_colour, screen.width // 2, 70)
    rendertextobject(infobox, bgcolour)
    p1pointdisplay = TextSquare("P1 Points: " + str(playerpoints[0]), font_colour, 80, 20)
    rendertextobject(p1pointdisplay, bgcolour)
    p2pointdisplay = TextSquare("P2 Points: " + str(playerpoints[1]), font_colour, screen.width - 80, 20)
    rendertextobject(p2pointdisplay, bgcolour)

    # render grid
    drawgrid()

    # render tiles
    for i in range(len(tiles[curplayer])):
        rendertile(tiles[curplayer][i], "white")
    for i in range(len(tiles[(curplayer+1)%2])):
        rendertile(tiles[(curplayer+1)%2][i], (102, 102, 102))

    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(100) 

pygame.quit()