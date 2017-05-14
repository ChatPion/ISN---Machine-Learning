import pygame
from pygame.locals import *
from shoot_game import Game, Actions, Status

def render(array, fenetre):
    origin = (320, 256)
    baseW, baseH = 64, -64
    
    for sprite, coords in array:
        fenetre.blit(sprite, (origin[0] + coords[0] * baseW, origin[1] + coords[1] * baseH))
    
    pygame.display.flip()

pygame.init()
game = Game(0.2, 5)

fenetre = pygame.display.set_mode((64*(2*game.width + 1), 64*5))
perso = pygame.image.load("perso3.png").convert_alpha()
bullet = pygame.image.load("bullet.png").convert_alpha()
shieldext = pygame.image.load("shieldext.png").convert_alpha()
shieldint = pygame.image.load("shieldint.png").convert_alpha()
to_blit = [shieldext, shieldint]

    
bullet_list = []
new_jump = 0
jump_diff = 0
t = 0
nb_hit = 0
frames_per_update = 10
chosen_action = Actions.STAND
continuer = 1
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = 0
        if event.type == KEYDOWN:
            if event.key == K_UP:
                chosen_action = Actions.JUMP

    fenetre.fill((0, 0, 0))
    dt = t % frames_per_update
    
    if dt == 0: # Update logic here
        old_jump = game.is_jumping
        game.tick(chosen_action)
        new_jump = game.is_jumping
        jump_diff = new_jump - old_jump
        chosen_action = Actions.STAND        
        bullet_list = []
        for i in game.bullets:
            bullet_list += [(i[0], i[1])]
        for i in game.deadbullets:
            bullet_list += [(i[0], i[1])]

    if game.player_status == Status.HIT:
        fenetre.blit(bullet, (0, 0))
        nb_hit +=1
    elif game.player_status == Status.SHIELD_HIT:
        fenetre.blit(shieldint, (0, 0))
    
    dt = frames_per_update - dt
    
    render_list = []
    for x, dir in bullet_list:
        render_list += [(bullet, (x - dir * dt / frames_per_update, 0))]#(x - dir / (dt + 1), 0))] 
    
    perso_coords = (0, new_jump - jump_diff * dt / frames_per_update)#jump_diff / (dt + 1))
    
    render_list += [(perso, perso_coords)]
    for i in range(len(game.shields)):
        if game.shields[i] == 0:
            render_list += [(to_blit[i], perso_coords)]
            break


    pygame.time.Clock().tick(60)
    t += 1

    render(render_list, fenetre)
print(nb_hit//frames_per_update)
