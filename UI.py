import pygame
from pygame.locals import *
pygame.init()

fenetre = pygame.display.set_mode((640, 480))
perso = pygame.image.load("perso.png").convert()
fenetre.blit(perso, (300, 380))
pygame.display.flip()
is_jumping = 0
continuer = 1
while continuer:
    if is_jumping == 0:
        is_jumping = 2
    else:
        is_jumping -= 1
        
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = 0
            
    pygame.display.flip()
    if is_jumping == 0:
        fenetre.blit(perso, (300, 380))
    elif game.is_jumping == 1:
        fenetre.blit(perso, (300, 280))
    else:
        fenetre.blit(perso, (300, 180))
    pygame.display.flip()
    
