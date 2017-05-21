import pygame
from pygame.locals import *
from shoot_game import Game, Actions, Status
from q_learning import Agent, load_agent, game_to_state, train
from math import floor

def render(array, fenetre):
    origin = (320, 256)
    global baseW, baseH
    
    for sprite, coords in array:
        fenetre.blit(sprite, (origin[0] + coords[0] * baseW, origin[1] + coords[1] * baseH))
    
    pygame.display.flip()

#train('save_file', training_params={'cycle_nb': 200})

baseW, baseH = 64, -64
pygame.init()

agent, game = load_agent('save_file.json')
game.probability = 0.33

font = pygame.font.SysFont("arial", 30)
text = font.render("HIT !", True, (255, 0, 0))
fenetre = pygame.display.set_mode((64*(2*game.width + 1), 320))
perso = pygame.image.load("imgs/perso3.png").convert_alpha()
bullet = pygame.image.load("imgs/bullet.png").convert_alpha()
shieldint = pygame.image.load("imgs/shieldint.png").convert_alpha()
shieldext = pygame.image.load("imgs/shieldext.png").convert_alpha()
shieldboth = pygame.image.load("imgs/shieldboth.png").convert_alpha()
to_blit = [shieldboth, shieldint, shieldext]

bullet_list = []
new_jump = 0
jump_diff = 0
t = 0

frames_per_update = 7

continuer = 1
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = 0

    fenetre.fill((0, 0, 0))
    dt = t % frames_per_update
    
    if dt == 0: # Update logic here
        old_jump = game.is_jumping
        state = game_to_state(game)
        chosen_action = agent.choose_best_action(state)
        
        game.tick(chosen_action)
        new_jump = game.is_jumping
        
        jump_diff = new_jump - old_jump
        
        bullet_list = []
        for i in game.bullets:
            bullet_list += [(i[0], i[1])]
        for i in game.deadbullets:
            bullet_list += [(i[0], i[1])]
        proportion = (floor(100000*game.nb_hit/game.shot_bullets)/100) if game.shot_bullets > 0 else 0
        message = str(proportion) + "‰"
        disp_hits = font.render(message, True, (255, 255, 255))
            

    if game.player_status == Status.HIT and dt <= ((frames_per_update*2)//3):
        fenetre.blit(text, ((11 * 64) // 2 - text.get_width()//2, 160 - text.get_height()//2))

    fenetre.blit(disp_hits, ((11*64) - disp_hits.get_width(), 0))
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
    for i in range(len(game.shields)):
        for j in range(game.shields_cooldown[i] - game.shields[i]):
            render_list += [(to_blit[2-i], (j - game.width, i))]
    


    pygame.time.Clock().tick(60)
    t += 1

    render(render_list, fenetre)

    
