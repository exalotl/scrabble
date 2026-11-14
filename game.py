import pygame
import copy
import random
from dawg import *

################################# functions
def rendertextobject(ob, colour, game):
    centred_rect = ob.Surface.get_rect(center=ob.Rect.center)
    pygame.draw.rect(game.screen, colour, ob.Rect)
    game.screen.blit(ob.Surface, centred_rect)

def rendertile(tl, colour, game):
    centred_rect = tl.Surface.get_rect(center=tl.Rect.center)
    pygame.draw.rect(game.screen, colour, tl.Rect)
    game.screen.blit(tl.Surface, centred_rect)
    if tl.Letter in "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z -".split(" "):
        game.screen.blit(tl.ScoreSurface, (centred_rect.x + 15, centred_rect.y + 15) )

def drawgrid(game):

    for i in range(15):
        for j in range(15):
            cell = Tile(game.grid[i][j], game.gridx + game.tile_size*j, game.gridy+ game.tile_size*i, game)
            if cell.Letter == "":
                if game.lettermult[i][j] == 2:
                    cell.changemodifier("2L", game)
                    rendertile(cell, (80, 118, 191), game)
                elif game.lettermult[i][j] == 3:
                    cell.changemodifier("3L", game)
                    rendertile(cell, (23, 62, 138), game)
                elif game.wordmult[i][j] == 2:
                    cell.changemodifier("2W", game)
                    rendertile(cell, (199, 116, 109), game)
                elif game.wordmult[i][j] == 3:
                    cell.changemodifier("3W", game)
                    rendertile(cell, (110, 23, 16), game)
                else:
                    rendertile(cell, game.bgcolour, game)
            elif game.blankpos[i][j] == True:
                cell.Points = 0
                cell.ScoreSurface = game.font2.render(str(cell.Points), True, game.font_colour)
                rendertile(cell, (200, 200, 100), game)
            else:
                rendertile(cell,(200, 200, 100), game)
            pygame.draw.rect(game.screen, "black", cell.Rect, 1)

            #pygame.draw.rect(screen, (0, 0, 0), 
            #    [gridx + tile_size*j, gridy+ tile_size*i, tile_size, tile_size], 1)
    grid_size = 15*game.tile_size
    pygame.draw.rect(game.screen, (0, 0, 0), 
                 [game.gridx, game.gridy, grid_size, grid_size], 2)

def processgrid(game): # return points or if invalid display error message and return -1 (bonus is handled in submit func)
    horicounted = [[False for i in range(15)] for j in range(15)]
    verticounted = [[False for i in range(15)] for j in range(15)]
    words = []
    newpoints = 0
    throughmiddle = False

    for i in range(15):
        for j in range(15):
            # hori check
            if game.newgrid[i][j] != game.grid[i][j] and not horicounted[i][j]:
                if (j != 0 and game.newgrid[i][j-1] != "") or (j != 14 and game.newgrid[i][j+1] != ""): # avoid out of bounds error
                    wordpoints = 0
                    multiplier = 1
                    connected = False
                    k = j
                    while k > 0 and game.newgrid[i][k-1] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and game.newgrid[i][k] != "":
                        curword += game.newgrid[i][k]
                        horicounted[i][k] = True

                        multiplier *= game.wordmult[i][k]
                        if not game.blankpos[i][k]:
                            wordpoints += game.lettermult[i][k] * game.score[game.newgrid[i][k]]

                        if game.newgrid[i][k] == game.grid[i][k]:
                            connected = True
                        if [i, k] == [7, 7]:
                            throughmiddle = True
                        k += 1
                    words.append(curword)
                    newpoints += multiplier * wordpoints
                    curword = ""
                    if game.turnshad != 0 and not connected:
                        game.infoboxtext = "Word must be connected"
                        return -1
            # verti check
            if game.newgrid[i][j] != game.grid[i][j] and not verticounted[i][j]:
                if (i != 0 and game.newgrid[i-1][j] != "") or (i != 14 and game.newgrid[i+1][j] != ""): # avoid out of bounds error
                    wordpoints = 0
                    multiplier = 1
                    connected = False
                    k = i
                    while k > 0 and game.newgrid[k-1][j] != "":
                        k -= 1
                    curword = ""
                    while k < 15 and game.newgrid[k][j] != "":
                        curword += game.newgrid[k][j]
                        verticounted[k][j] = True

                        multiplier *= game.wordmult[k][j]
                        if not game.blankpos[k][j]:
                            wordpoints += game.lettermult[k][j] * game.score[game.newgrid[k][j]]

                        if game.newgrid[k][j] == game.grid[k][j]:
                            connected = True
                        if [k, j] == [7, 7]:
                            throughmiddle = True
                        k += 1
                    words.append(curword)
                    newpoints += multiplier * wordpoints
                    curword = ""
                    if game.turnshad != 0 and not connected:
                        game.infoboxtext = "Word must be connected"
                        return -1

    if len(words) == 0:
        game.infoboxtext = "No words"
        return -1

    if not checkstraightline(game):
        game.infoboxtext = "Straight line needed"
        return -1
    
    if game.turnshad == 0 and throughmiddle == False:
        game.infoboxtext = "First word must go through middle"
        return -1

    for word in words:
        print(word, end= " , ")
    print()

    for word in words:
        if game.wordbank.search(word) == False:
            game.infoboxtext = word + " not in word list"
            return -1

    """
    game.infoboxtext = "Valid move: +" + str(newpoints)

    for word in words:
        if len(word) == 7:
            game.infoboxtext = "Bingo! +" + str(newpoints) + " +50"
            newpoints += 50
    """

    return newpoints


def endgame(game):
    p1change = 0
    p2change = 0

    newrack = []
    for i in range(len(game.tiles[game.curplayer])):
        row = round((game.tiles[game.curplayer][i].Rect.y - game.gridy) / game.tile_size)
        col = round((game.tiles[game.curplayer][i].Rect.x - game.gridx) / game.tile_size)

        if (row < 0 or row >= 15) or (col < 0 or col >= 15):
            newrack.append(game.tiles[game.curplayer][i].Letter)
    game.rack[game.curplayer] = copy.deepcopy(newrack)
    refreshtiles(game)

    for tl in game.tiles[0]:
        p1change -= tl.Points
    for tl in game.tiles[1]:
        p2change -= tl.Points

    game.playerpoints[0] += p1change
    game.playerpoints[1] += p2change

    if len(game.tiles[0]) == 0:
        p1change += p2change * -1
    elif len(game.tiles[1]) == 0:
            p2change += p1change * -1

    if game.playerpoints[0] > game.playerpoints[1]:
        game.infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ "  END: P1 wins"
    elif game.playerpoints[1] > game.playerpoints[0]:
        game.infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ " END: P2 wins"
    else:
        game.infoboxtext = "Final:  P1: "+str(p1change) + "  P2: " + str(p2change)+ " END: Draw"

    game.ended = True
    #running = False

def fillrack(player, game): # take in 0 or 1

    while len(game.rack[player]) < 7 and len(game.bag) != 0:
        game.rack[player].append(game.bag.pop())

    if len(game.rack[player]) == 0:
        endgame(game)

def refreshtiles(game):
    game.tiles[0] = []
    for i in range(len(game.rack[0])):
        game.tiles[0].append(Tile(game.rack[0][i], 50 * i, game.racky, game))

    game.tiles[1] = []
    for i in range(len(game.rack[1])):
        game.tiles[1].append(Tile(game.rack[1][i], game.screen.get_width() - (50 * i) - 60, game.racky, game))

def putback(game):
    for i in range(len(game.tiles[game.curplayer])):
        if game.curplayer == 0:
            game.tiles[game.curplayer][i].Rect.x = 50 * i
        else:
            game.tiles[game.curplayer][i].Rect.x = game.screen.get_width() - (50 * i) - 60
        game.tiles[game.curplayer][i].Rect.y = game.racky

def discard(game):

    if (len(game.bag) < 7):
        game.infoboxtext = "Not enough tiles in bag to discard tiles"
        return

    binhascontents = False
    newrack = []
    for i in range(len(game.tiles[game.curplayer])):
        if not game.tiles[game.curplayer][i].Rect.colliderect(game.bin):
            newrack.append(game.tiles[game.curplayer][i].Letter)
        else:
            binhascontents = True
    game.rack[game.curplayer] = copy.deepcopy(newrack)

    if not binhascontents:
        game.infoboxtext = "No tiles in bin"
        return

    fillrack(game.curplayer, game)
    refreshtiles(game)
    putback(game)
    game.infoboxtext = "P"+str(game.curplayer+1) + " discarded tiles"
    game.curplayer = (game.curplayer+1)%2 # does not increase turn counter
    game.skipcounter += 1
    if game.skipcounter == 6:
        endgame(game)


def removemodifiers(game):
    # remove modifiers that have been used
    for i in range(15):
        for j in range(15):
            if game.grid[i][j] != "":
                game.wordmult[i][j] = 1
                game.lettermult[i][j] = 1

def checkstraightline(game):
    first = "-"
    second = "-"

    for i in range(15):
        for j in range(15):
            if game.newgrid[i][j] != game.grid[i][j]:
                if first == "-":
                    first = [i, j]
                elif second == "-":
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

def submitpressed(game):
    res = processgrid(game)
    if res != -1:
        game.grid = copy.deepcopy(game.newgrid)
        newrack = []
        for i in range(len(game.tiles[game.curplayer])):
            row = round((game.tiles[game.curplayer][i].Rect.y - game.gridy) / game.tile_size)
            col = round((game.tiles[game.curplayer][i].Rect.x - game.gridx) / game.tile_size)

            if (row < 0 or row >= 15) or (col < 0 or col >= 15):
                newrack.append(game.tiles[game.curplayer][i].Letter)

        game.rack[game.curplayer] = copy.deepcopy(newrack)
        if len(game.rack[game.curplayer]) == 0:
            game.infoboxtext = "Bonus! +" + str(res) + " +50"
            res += 50
        else:
            game.infoboxtext = "Valid move +" + str(res)
        game.skipcounter =  0
        game.playerpoints[game.curplayer] += res

        fillrack(game.curplayer, game)
        refreshtiles(game)
        removemodifiers(game)

        putback(game)

        game.curplayer = (game.curplayer+1)%2
        game.turnshad += 1

def setblankletter(ev, game):
    mousepos = pygame.mouse.get_pos()
    for i in range(len(game.tiles[game.curplayer])):
        if game.tiles[game.curplayer][i].Changeable:
            if game.tiles[game.curplayer][i].Rect.collidepoint(mousepos):
                if ev.unicode.isalpha():
                    game.tiles[game.curplayer][i].changeletter(ev.unicode.upper(), game)
                    #print("trigger")
                    row = round((game.tiles[game.curplayer][i].Rect.y - game.gridy) / game.tile_size)
                    col = round((game.tiles[game.curplayer][i].Rect.x - game.gridx) / game.tile_size)
                    if (row >= 0 and row < 15) and (col >= 0 and col < 15):
                        game.newgrid[row][col] = game.tiles[game.curplayer][i].Letter



##################################################### classes


class Tile:
    def __init__(self, letter, spawnx, spawny, game):
        self.Letter = letter
        self.Surface = game.font1.render(letter, True, game.font_colour)
        self.Rect = self.Surface.get_rect()
        self.Rect.width = game.tile_size
        self.Rect.height = game.tile_size
        self.Rect.x = spawnx
        self.Rect.y = spawny

        self.Points = 0
        self.Changeable = False

        if letter == "-":
            self.Changeable = True

        if letter != "":
            self.Points = game.score[letter]
            self.ScoreSurface = game.font2.render(str(self.Points), True, game.font_colour)

    def changeletter(self, changeto, game):
        # change letter but not points, points should stay at 0
        if self.Changeable:
            self.Letter = changeto
            self.Surface = game.font1.render(self.Letter, True, game.font_colour)
            self.Points = game.score[self.Letter]
            #print(self.Letter)
    def changemodifier(self, changeto, game):
        self.Letter = changeto
        self.Surface = game.font2.render(self.Letter, True, game.font_colour)

class TextSquare:
    def __init__(self, text, colour, spawnx, spawny, game):
        self.Text = text
        self.Surface = game.font1.render(text, True, colour) ### font colour change
        self.Rect = self.Surface.get_rect()
        self.Rect.width += 25
        self.Rect.height += 25
        self.Rect.x = spawnx - self.Rect.width//2
        self.Rect.y = spawny - self.Rect.height//2


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((720, 800))
        self.clock = pygame.time.Clock()
        #running = Trues

        pygame.display.set_caption("Scrabble")

        self.font1 = pygame.font.Font("freesansbold.ttf", 20)
        self.font2 = pygame.font.Font("freesansbold.ttf", 15)
        self.initvariables()

        fillrack(0, self)
        fillrack(1, self)
        refreshtiles(self)


    def initvariables(self):
        self.grid = [["" for i in range(15)] for j in range(15)]
        self.newgrid = copy.deepcopy(self.grid)
        self.blankpos = [[False for i in range(15)] for j in range(15)]

        self.lettermult = [[1 for i in range(15)] for j in range(15)]
        for i in [1, 5, 9, 13]:
            for j in [1, 5,9, 13]:
                self.lettermult[i][j] = 3
        self.lettermult[1][1] = 1
        self.lettermult[1][13] = 1
        self.lettermult[13][1] = 1
        self.lettermult[13][13] = 1
        for i in [0, 14]:
            for j in [3, 11]:
                self.lettermult[i][j] = 2
                self.lettermult[j][i] = 2
        self.lettermult[2][6] = 2
        self.lettermult[2][8] = 2
        self.lettermult[3][7] = 2
        self.lettermult[14-2][6] = 2
        self.lettermult[14-2][8] = 2
        self.lettermult[14-3][7] = 2
        self.lettermult[6][2] = 2
        self.lettermult[7][3] = 2
        self.lettermult[8][2] = 2
        self.lettermult[6][14-2] = 2
        self.lettermult[7][14-3] = 2
        self.lettermult[8][14-2] = 2
        self.lettermult[6][6] = 2
        self.lettermult[6][8] = 2
        self.lettermult[8][8] = 2
        self.lettermult[8][6] = 2


        self.wordmult = [[1 for i in range(15)] for j in range(15)]
        for i in [0, 7, 14]:
            for j in [0, 7, 14]:
                self.wordmult[i][j] = 3
        for i in[1, 2, 3, 4, 10, 11, 12, 13]:
            self.wordmult[i][i] = 2
            self.wordmult[i][14-i] = 2
        self.wordmult[7][7] = 2

        self.score = {"A":1, "B":3, "C":3, "D":2, "E":1, "F":4, 
                "G":2, "H":4, "I":1, "J":8, "K":5, "L":1,
                "M":3, "N":1, "O":1, "P":3, "Q":10, "R":1,
                "S":1, "T":1, "U":1, "V":4, "W":4, "X":8,
                "Y":4, "Z":10, "-":0}


        self.bag = [
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
        self.bag = "B E C A U S E B E C A U S E B E C A U S E".split(" ")

        self.tiles = [[], []] # p1, p2

        #random.shuffle(self.bag)

        self.rack = [[], []]
        self.tile_size = 37
        self.font_colour = (0, 0, 0)
        self.gridx = self.screen.get_width() // 2 - (7.5*self.tile_size)
        self.gridy = 170
        self.leavingposx = 0
        self.leavingposy = 0
        self.racky = 750
        self.bgcolour = "grey"
        self.infoboxtext = ""
        self.curplayer = 0 
        self.playerpoints = [0, 0]
        self.turnshad = 0
        self.skipcounter = 0
        self.ended = False

        self.offsetx = 0
        self.offsety = 0
        self.leavingrow = -1
        self.leavingcol = -1
        self.dragging = -1

        ### self.[displayobject]s are not here, they are in step

        self.wordbank = DAWG()
        self.wordbank.build("CSW24.txt")



    def step(self):
        # main game loop here
        # variables: dragging, self.leavingrow, self.leavingcol

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #running = False
                pygame.quit() # ------> CHECK IF THIS OK 

            elif event.type == pygame.MOUSEBUTTONDOWN:
                ################# tile dragging
                for i in range(len(self.tiles[self.curplayer])):
                    if self.tiles[self.curplayer][i].Rect.collidepoint(event.pos):
                        if event.button == 1:
                            self.dragging = i
                            mouse_x, mouse_y = event.pos
                            self.offsetx = self.tiles[self.curplayer][i].Rect.x - mouse_x
                            self.offsety = self.tiles[self.curplayer][i].Rect.y - mouse_y
                            self.leavingrow = round((self.tiles[self.curplayer][self.dragging].Rect.y - self.gridy) / self.tile_size)
                            self.leavingcol = round((self.tiles[self.curplayer][self.dragging].Rect.x - self.gridx) / self.tile_size)

                if self.submitbutton.Rect.collidepoint(event.pos):
                    submitpressed(self)


                if self.skipbutton.Rect.collidepoint(event.pos):
                    putback(self)
                    self.infoboxtext = "P"+str(self.curplayer+1) + " skipped"
                    self.curplayer = (self.curplayer+1)%2
                    self.newgrid = copy.deepcopy(self.grid)
                    self.skipcounter += 1
                    if self.skipcounter == 6:
                        endgame(self)
                    # if turn skipped, do not increase turn counter

                if self.discardbutton.Rect.collidepoint(event.pos):
                    discard(self)


            elif event.type == pygame.MOUSEBUTTONUP:
                ########### tile put down
                if self.dragging != -1:
                    row = round((self.tiles[self.curplayer][self.dragging].Rect.y - self.gridy) / self.tile_size)
                    col = round((self.tiles[self.curplayer][self.dragging].Rect.x - self.gridx) / self.tile_size)
                    #print(row, col)

                    if (self.leavingrow >= 0 and self.leavingrow < 15) and (self.leavingcol >= 0 and self.leavingcol < 15):
                        self.newgrid[self.leavingrow][self.leavingcol] = ""
                        if self.tiles[self.curplayer][self.dragging].Changeable:
                            self.blankpos[self.leavingrow][self.leavingcol] = False
                    if (row >= 0 and row < 15) and (col >= 0 and col < 15):
                        if (self.newgrid[row][col] == ""):
                            self.tiles[self.curplayer][self.dragging].Rect.x = col*self.tile_size + self.gridx
                            self.tiles[self.curplayer][self.dragging].Rect.y = row*self.tile_size + self.gridy
                            self.newgrid[row][col] = self.tiles[self.curplayer][self.dragging].Letter
                            if self.tiles[self.curplayer][self.dragging].Changeable:
                                self.blankpos[row][col] = True
                                #print("trigger")
                        else:
                            self.tiles[self.curplayer][self.dragging].Rect.y = self.racky
                self.dragging = -1


            elif event.type == pygame.MOUSEMOTION:
                if self.dragging != -1:
                    mouse_x, mouse_y = event.pos
                    self.tiles[self.curplayer][self.dragging].Rect.x = self.offsetx + mouse_x
                    self.tiles[self.curplayer][self.dragging].Rect.y = self.offsety + mouse_y


            elif event.type == pygame.KEYDOWN:
                setblankletter(event, self)



        self.screen.fill(self.bgcolour)


        #render buttons / other
        self.p1pointdisplay = TextSquare("P1 Points: " + str(self.playerpoints[0]), self.font_colour, 80, 20, self)
        rendertextobject(self.p1pointdisplay, self.bgcolour, self)
        self.p2pointdisplay = TextSquare("P2 Points: " + str(self.playerpoints[1]), self.font_colour, self.screen.get_width() - 80, 20, self)
        rendertextobject(self.p2pointdisplay, self.bgcolour, self)
        self.submitbutton = TextSquare("Submit", "white", 600, 70, self)
        rendertextobject(self.submitbutton, (128, 58, 45), self)
        self.playerdisplay = TextSquare("Player " + str(self.curplayer+1) + " turn", self.font_colour, self.screen.get_width() // 2, 20, self)
        rendertextobject(self.playerdisplay, self.bgcolour, self)
        self.bagdisplay = TextSquare("Tiles left in bag: " + str(len(self.bag)), self.font_colour, 100, 50, self)
        rendertextobject(self.bagdisplay, self.bgcolour, self)
        self.skipdisplay = TextSquare("Skip counter (end at 6): " + str(self.skipcounter), self.font_colour, 570, 130, self)
        rendertextobject(self.skipdisplay, self.bgcolour, self)
        self.infobox = TextSquare(self.infoboxtext, self.font_colour, 200, 80, self)
        rendertextobject(self.infobox, self.bgcolour, self)
        self.skipbutton = TextSquare("Skip", "white", 500, 70, self)
        rendertextobject(self.skipbutton, (50, 58, 45), self)
        self.discardbutton = TextSquare("Discard", "white", 60, 130, self)
        rendertextobject(self.discardbutton, (50, 58, 45), self)
        self.bin = pygame.Rect(120, 105, 300, 50) 
        pygame.draw.rect(self.screen, (100, 100, 100), self.bin)



        # render grid
        drawgrid(self)

        # render tiles
        for i in range(len(self.tiles[self.curplayer])):
            rendertile(self.tiles[self.curplayer][i], "white", self)
        for i in range(len(self.tiles[(self.curplayer+1)%2])):
            rendertile(self.tiles[(self.curplayer+1)%2][i], (102, 102, 102), self)

        
        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(100) 
