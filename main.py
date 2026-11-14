import pygame
import copy
import random
from dawg import *
from game import *


game = Game()


running = True
while running:
    if game.ended:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    else:
        game.step()
pygame.quit()