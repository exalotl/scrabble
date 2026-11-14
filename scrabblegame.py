"""
self contained, only game ver
(first implementation)

also bingo / bonnus is wrong - it +50 when word len is 7 not when all tiles used
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

        self.Points = 0
        self.Changeable = False

        if letter == "-":
            self.Changeable = True

        if letter != "":
            self.Points = score[letter]
            self.ScoreSurface = font2.render(str(self.Points), True, font_colour)

    def changeletter(self, changeto):
        # change letter but not points, points should stay at 0
        if self.Changeable:
            self.Letter = changeto
            self.Surface = font1.render(self.Letter, True, font_colour)
            self.Points = score[self.Letter]
            #print(self.Letter)
    def changemodifier(self, changeto):
        self.Letter = changeto
        self.Surface = font2.render(self.Letter, True, font_colour)

class TextSquare:
    def __init__(self, text, colour, spawnx, spawny):
        self.Text = text
        self.Surface = font1.render(text, True, colour) ### font colour change
        self.Rect = self.Surface.get_rect()
        self.Rect.width += 25
        self.Rect.height += 25
        self.Rect.x = spawnx - self.Rect.width//2
        self.Rect.y = spawny - self.Rect.height//2

################## variables
grid = [["" for i in range(15)] for j in range(15)]
#grid[5][5] = "A"

newgrid = copy.deepcopy(grid)
blankpos = [[False for i in range(15)] for j in range(15)]

lettermult = [[1 for i in range(15)] for j in range(15)]
for i in [1, 5, 9, 13]:
    for j in [1, 5,9, 13]:
        lettermult[i][j] = 3
lettermult[1][1] = 1
lettermult[1][13] = 1
lettermult[13][1] = 1
lettermult[13][13] = 1
for i in [0, 14]:
    for j in [3, 11]:
        lettermult[i][j] = 2
        lettermult[j][i] = 2
lettermult[2][6] = 2
lettermult[2][8] = 2
lettermult[3][7] = 2
lettermult[14-2][6] = 2
lettermult[14-2][8] = 2
lettermult[14-3][7] = 2
lettermult[6][2] = 2
lettermult[7][3] = 2
lettermult[8][2] = 2
lettermult[6][14-2] = 2
lettermult[7][14-3] = 2
lettermult[8][14-2] = 2
lettermult[6][6] = 2
lettermult[6][8] = 2
lettermult[8][8] = 2
lettermult[8][6] = 2


wordmult = [[1 for i in range(15)] for j in range(15)]
for i in [0, 7, 14]:
    for j in [0, 7, 14]:
        wordmult[i][j] = 3
for i in[1, 2, 3, 4, 10, 11, 12, 13]:
    wordmult[i][i] = 2
    wordmult[i][14-i] = 2
wordmult[7][7] = 2

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
    "K", "J", "X", "Q", "Z",
    "-", "-"
]


#bag = ["C", "A", "T", "S", "C", "A", "T", "S", "C", "A", "T", "S", "C", "A", "T", "S", ]
#bag = "B E C A U S E B E C A U S E B E C A U S E".split(" ")

tiles = [[], []] # p1, p2
dragging = -1

random.shuffle(bag)

rack = [[], []]
tile_size = 37
font_colour = (0, 0, 0)
gridx = screen.get_width() // 2 - (7.5*tile_size)
gridy = 170
leavingposx = 0
leavingposy = 0
racky = 750
bgcolour = "grey"
infoboxtext = ""
curplayer = 0 
playerpoints = [0, 0]
turnshad = 0
skipcounter = 0
gameended = False

wordbank = DAWG()
wordbank.build("CSW24.txt")

#################### functions
def rendertextobject(ob, colour):
    centred_rect = ob.Surface.get_rect(center=ob.Rect.center)
    pygame.draw.rect(screen, colour, ob.Rect)
    screen.blit(ob.Surface, centred_rect)

def rendertile(tl, colour):
    centred_rect = tl.Surface.get_rect(center=tl.Rect.center)
    pygame.draw.rect(screen, colour, tl.Rect)
    screen.blit(tl.Surface, centred_rect)
    if tl.Letter in "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z -".split(" "):
        screen.blit(tl.ScoreSurface, (centred_rect.x + 15, centred_rect.y + 15) )

def drawgrid():

    for i in range(15):
        for j in range(15):
            cell = Tile(grid[i][j], gridx + tile_size*j, gridy+ tile_size*i)
            if cell.Letter == "":
                if lettermult[i][j] == 2:
                    cell.changemodifier("2L")
                    rendertile(cell, (80, 118, 191))
                elif lettermult[i][j] == 3:
                    cell.changemodifier("3L")
                    rendertile(cell, (23, 62, 138))
                elif wordmult[i][j] == 2:
                    cell.changemodifier("2W")
                    rendertile(cell, (199, 116, 109))
                elif wordmult[i][j] == 3:
                    cell.changemodifier("3W")
                    rendertile(cell, (110, 23, 16))
                else:
                    rendertile(cell, bgcolour)
            elif blankpos[i][j] == True:
                cell.Points = 0
                cell.ScoreSurface = font2.render(str(cell.Points), True, font_colour)
                rendertile(cell, (200, 200, 100))
            else:
                rendertile(cell,(200, 200, 100))
            pygame.draw.rect(screen, "black", cell.Rect, 1)

            #pygame.draw.rect(screen, (0, 0, 0), 
            #    [gridx + tile_size*j, gridy+ tile_size*i, tile_size, tile_size], 1)
    grid_size = 15*tile_size
    pygame.draw.rect(screen, (0, 0, 0), 
                 [gridx, gridy, grid_size, grid_size], 2)

def processgrid(): # return points or -1 if invalid
    global infoboxtext
    horicounted = [[False for i in range(15)] for j in range(15)]
    verticounted = [[False for i in range(15)] for j in range(15)]
    words = []
    newpoints = 0
    throughmiddle = False

    for i in range(15):
        for j in range(15):
            # hori check
            if newgrid[i][j] != grid[i][j] and not horicounted[i][j]:
                if (j != 0 and newgrid[i][j-1] != "") or (j != 14 and newgrid[i][j+1] != ""): # avoid out of bounds error
                    wordpoints = 0
                    multiplier = 1
                    connected = False
                    k = j
                    while k > 0 and newgrid[i][k-1] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and newgrid[i][k] != "":
                        curword += newgrid[i][k]
                        horicounted[i][k] = True

                        multiplier *= wordmult[i][k]
                        if not blankpos[i][k]:
                            wordpoints += lettermult[i][k] * score[newgrid[i][k]]

                        if newgrid[i][k] == grid[i][k]:
                            connected = True
                        if [i, k] == [7, 7]:
                            throughmiddle = True
                        k += 1
                    words.append(curword)
                    newpoints += multiplier * wordpoints
                    curword = ""
                    if turnshad != 0 and not connected:
                        infoboxtext = "Word must be connected"
                        return -1
            # verti check
            if newgrid[i][j] != grid[i][j] and not verticounted[i][j]:
                if (i != 0 and newgrid[i-1][j] != "") or (i != 14 and newgrid[i+1][j] != ""): # avoid out of bounds error
                    wordpoints = 0
                    multiplier = 1
                    connected = False
                    k = i
                    while k > 0 and newgrid[k-1][j] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and newgrid[k][j] != "":
                        curword += newgrid[k][j]
                        verticounted[k][j] = True

                        multiplier *= wordmult[k][j]
                        if not blankpos[k][j]:
                            wordpoints += lettermult[k][j] * score[newgrid[k][j]]

                        if newgrid[k][j] == grid[k][j]:
                            connected = True
                        if [k, j] == [7, 7]:
                            throughmiddle = True
                        k += 1
                    words.append(curword)
                    newpoints += multiplier * wordpoints
                    curword = ""
                    if turnshad != 0 and not connected:
                        infoboxtext = "Word must be connected"
                        return -1

    if len(words) == 0:
        infoboxtext = "No words"
        return -1

    if not checkstraightline():
        infoboxtext = "Straight line needed"
        return -1
    
    if turnshad == 0 and throughmiddle == False:
        infoboxtext = "First word must go through middle"
        return -1

    for word in words:
        print(word, end= " , ")
    print()

    for word in words:
        if wordbank.search(word) == False:
            infoboxtext = word + " not in word list"
            return -1
        
    infoboxtext = "Valid move: +" + str(newpoints)

    for word in words:
        if len(word) == 7:
            infoboxtext = "Bingo! +" + str(newpoints) + " +50"
            newpoints += 50

    return newpoints

def endgame():
    global infoboxtext
    global running
    global gameended
    p1change = 0
    p2change = 0

    newrack = []
    for i in range(len(tiles[curplayer])):
        row = round((tiles[curplayer][i].Rect.y - gridy) / tile_size)
        col = round((tiles[curplayer][i].Rect.x - gridx) / tile_size)

        if (row < 0 or row >= 15) or (col < 0 or col >= 15):
            newrack.append(tiles[curplayer][i].Letter)
    rack[curplayer] = copy.deepcopy(newrack)
    refreshtiles()

    for tl in tiles[0]:
        p1change -= tl.Points
    for tl in tiles[1]:
        p2change -= tl.Points

    playerpoints[0] += p1change
    playerpoints[1] += p2change

    if len(tiles[0]) == 0:
        p1change += p2change * -1
    elif len(tiles[1]) == 0:
            p2change += p1change * -1

    if playerpoints[0] > playerpoints[1]:
        infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ "  END: P1 wins"
    elif playerpoints[1] > playerpoints[0]:
        infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ " END: P2 wins"
    else:
        infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ " END: Draw"

    gameended = True
    #running = False

def fillrack(player): # take in 0 or 1

    """
    for l in bag:
        print(l, end = " ")
    print()
    """
    
    while len(rack[player]) < 7 and len(bag) != 0:
        rack[player].append(bag.pop())

    if len(rack[player]) == 0:
        endgame()

def refreshtiles():
    tiles[0] = []
    for i in range(len(rack[0])):
        tiles[0].append(Tile(rack[0][i], 50 * i, racky))

    tiles[1] = []
    for i in range(len(rack[1])):
        tiles[1].append(Tile(rack[1][i], screen.get_width() - (50 * i) - 60, racky))

def putback():
    for i in range(len(tiles[curplayer])):
        if curplayer == 0:
            tiles[curplayer][i].Rect.x = 50 * i
        else:
            tiles[curplayer][i].Rect.x = screen.get_width() - (50 * i) - 60
        tiles[curplayer][i].Rect.y = racky

def discard():
    global rack
    global infoboxtext
    global curplayer
    global skipcounter

    if (len(bag) < 7):
        infoboxtext = "Not enough tiles in bag to discard tiles"
        return

    binhascontents = False
    newrack = []
    for i in range(len(tiles[curplayer])):
        if not tiles[curplayer][i].Rect.colliderect(bin):
            newrack.append(tiles[curplayer][i].Letter)
        else:
            binhascontents = True
    rack[curplayer] = copy.deepcopy(newrack)

    if not binhascontents:
        infoboxtext = "No tiles in bin"
        return

    fillrack(curplayer)
    refreshtiles()
    putback()
    infoboxtext = "P"+str(curplayer+1) + " discarded tiles"
    curplayer = (curplayer+1)%2 # does not increase turn counter
    skipcounter += 1
    if skipcounter == 6:
        endgame()

def removemodifiers():
    # remove modifiers that have been used
    for i in range(15):
        for j in range(15):
            if grid[i][j] != "":
                wordmult[i][j] = 1
                lettermult[i][j] = 1

def checkstraightline():
    first = "nothing here lol"
    second = "me neither lol"

    for i in range(15):
        for j in range(15):
            if newgrid[i][j] != grid[i][j]:
                if first == "nothing here lol":
                    first = [i, j]
                elif second == "me neither lol":
                    if i == first[0]:
                        second = "row"
                    elif j == first[1]:
                        second = "col"
                    else:
                        return False
                else:
                    if second == "row" and i != first[0]:
                        return False
                    elif second == "col" and j != first[1]:
                        return False
    return True
    
################# pre loop code
fillrack(0)
fillrack(1)
refreshtiles()

################  main loop
while running:

    if gameended:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(tiles[curplayer])):
                    if tiles[curplayer][i].Rect.collidepoint(event.pos):
                        if event.button == 1:
                            dragging = i
                            mouse_x, mouse_y = event.pos
                            offset_x = tiles[curplayer][i].Rect.x - mouse_x
                            offset_y = tiles[curplayer][i].Rect.y - mouse_y
                            leavingrow = round((tiles[curplayer][dragging].Rect.y - gridy) / tile_size)
                            leavingcol = round((tiles[curplayer][dragging].Rect.x - gridx) / tile_size)

                if submitbutton.Rect.collidepoint(event.pos):
                    # submit button pressed
                    res = processgrid()
                    if res != -1:
                        skipcounter =  0
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
                        removemodifiers()

                        putback()

                        curplayer = (curplayer+1)%2
                        turnshad += 1
                if skipbutton.Rect.collidepoint(event.pos):
                    putback()
                    infoboxtext = "P"+str(curplayer+1) + " skipped"
                    curplayer = (curplayer+1)%2
                    newgrid = copy.deepcopy(grid)
                    skipcounter += 1
                    if skipcounter == 6:
                        endgame()
                    # if turn skipped, do not increase turn counter
                if discardbutton.Rect.collidepoint(event.pos):
                    discard()


            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging != -1:
                    row = round((tiles[curplayer][dragging].Rect.y - gridy) / tile_size)
                    col = round((tiles[curplayer][dragging].Rect.x - gridx) / tile_size)
                    #print(row, col)

                    if (leavingrow >= 0 and leavingrow < 15) and (leavingcol >= 0 and leavingcol < 15):
                        newgrid[leavingrow][leavingcol] = ""
                        if tiles[curplayer][dragging].Changeable:
                            blankpos[leavingrow][leavingcol] = False
                    if (row >= 0 and row < 15) and (col >= 0 and col < 15):
                        if (newgrid[row][col] == ""):
                            tiles[curplayer][dragging].Rect.x = col*tile_size + gridx
                            tiles[curplayer][dragging].Rect.y = row*tile_size + gridy
                            newgrid[row][col] = tiles[curplayer][dragging].Letter
                            if tiles[curplayer][dragging].Changeable:
                                blankpos[row][col] = True
                                #print("trigger")
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
                mousepos = pygame.mouse.get_pos()
                for i in range(len(tiles[curplayer])):
                    if tiles[curplayer][i].Changeable:
                        if tiles[curplayer][i].Rect.collidepoint(mousepos):
                            if event.unicode in "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(" "):
                                tiles[curplayer][i].changeletter(event.unicode)
                                #print("trigger")
                                row = round((tiles[curplayer][i].Rect.y - gridy) / tile_size)
                                col = round((tiles[curplayer][i].Rect.x - gridx) / tile_size)
                                if (row >= 0 and row < 15) and (col >= 0 and col < 15):
                                    newgrid[row][col] = tiles[curplayer][i].Letter




        screen.fill(bgcolour)

        # RENDER HERE

        #render buttons / other
        p1pointdisplay = TextSquare("P1 Points: " + str(playerpoints[0]), font_colour, 80, 20)
        rendertextobject(p1pointdisplay, bgcolour)
        p2pointdisplay = TextSquare("P2 Points: " + str(playerpoints[1]), font_colour, screen.get_width() - 80, 20)
        rendertextobject(p2pointdisplay, bgcolour)
        submitbutton = TextSquare("Submit", "white", 600, 70)
        rendertextobject(submitbutton, (128, 58, 45))
        playerdisplay = TextSquare("Player " + str(curplayer+1) + " turn", font_colour, screen.get_width() // 2, 20)
        rendertextobject(playerdisplay, bgcolour)
        bagdisplay = TextSquare("Tiles left in bag: " + str(len(bag)), font_colour, 100, 50)
        rendertextobject(bagdisplay, bgcolour)
        skipdisplay = TextSquare("Skip counter (end at 6): " + str(skipcounter), font_colour, 570, 130)
        rendertextobject(skipdisplay, bgcolour)
        infobox = TextSquare(infoboxtext, font_colour, 200, 80)
        rendertextobject(infobox, bgcolour)
        skipbutton = TextSquare("Skip", "white", 500, 70)
        rendertextobject(skipbutton, (50, 58, 45))
        discardbutton = TextSquare("Discard", "white", 60, 130)
        rendertextobject(discardbutton, (50, 58, 45))
        bin = pygame.Rect(120, 105, 300, 50) 
        pygame.draw.rect(screen, (100, 100, 100), bin)



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