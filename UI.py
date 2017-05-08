import pygame
from pygame.locals import *
pygame.init()
game = Game(1/4, 5, [0, 0])
fenetre = pygame.display.set_mode((64*(2*game.width + 1), 320))
perso = pygame.image.load("perso.png").convert()
bullet = pygame.image.load("bullet.png").convert_alpha()
fenetre.blit(perso, (320, 256))
pygame.display.flip()
continuer = 1
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = 0
            
    pygame.display.flip()
    if game.is_jumping == 0:
        fenetre.blit(perso, (320, 256))
    elif game.is_jumping == 1:
        fenetre.blit(perso, (320, 192))
    else:
        fenetre.blit(perso, (320, 128))
    for i in game.bullets:
        fenetre.blit(bullet, (64*(5+i[0]), 256))
    for i in game.deadbullets:
        fenetre.blit(bullet, (64*(5+i[0]), 256))
    pygame.display.flip()
    
