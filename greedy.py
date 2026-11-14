from dawg import *
from scrabblegame import *

gaddag = DAWG()
gaddag.build("wordbank_rpf.txt")
#print(gaddag.search("AA"))
#print(gaddag.search("T#HYMECTOMY"))
#print(gaddag.search(",,,"))
#print(gaddag.search("A#ARDWOLVES"))


"""
# make scrabble in pygame


setup:
do once for 'across' plays then transpose and do for 'below'
--- go through every tile, if there are perpendicular tiles (eg. above or below for across play) and mark possible tiles
--- [NOW UNNECESSARY] for these tiles, mark how many extra points it would be (don't include tile itself, this get counted during move gen)

move gen:
do once for across and once for below
for every possible starting adjacent tile:
--- recursively search valid moves by checking if tiles from bag are valid moves (check against marked possible tiles for that square) 
--- score as you go
--- for each step during recursion, if # is possible then switch to right side and continue recursive search

decision:
--- greedy for now (develop more later)

after decision made, repeat setup for surrounding tiles of move

"""

alphabet = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(" ")

horipossible = [[alphabet for i in range(15)] for j in range(15)] # possible tiles when generating horizontal (from perpendicularly vertical words that would be made)
vertipossible = [[alphabet for i in range(15)] for j in range(15)] # possible tiles when generating vertical (from perpendicularly horizontal words that would be made)

def markpossible():
    #######

def movegen(): # find all possible plays
    #######