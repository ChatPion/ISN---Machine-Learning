import pygame
from pygame.locals import *
from shoot_game import Game, Actions, Status
from q_learning import Agent, load_agent, game_to_state, train
from math import floor


class UI:
    def __init__(self, game):
        self.baseW = 64
        self.baseH = 64

        pygame.init()

        self.font = pygame.font.SysFont("arial", self.baseH)
        self.text = self.font.render("HIT !", True, (255, 0, 0))
        self.fenetre = pygame.display.set_mode((self.baseW * (2 * game.width + 1), self.baseH * 5))
        self.perso = pygame.image.load("imgs/frog.png").convert_alpha()
        self.bullet = pygame.image.load("imgs/fireball.png").convert_alpha()
        shieldint = pygame.image.load("imgs/shieldint.png").convert_alpha()
        shieldext = pygame.image.load("imgs/shieldext.png").convert_alpha()
        shieldboth = pygame.image.load("imgs/shieldboth.png").convert_alpha()
        self.to_blit = [shieldboth, shieldint, shieldext]

        self.disp_hits = None

        self.bullet_list = []
        self.new_jump = 0
        self.jump_diff = 0

        self.game = game

    def render(self, array):
        origin = (self.baseW * self.game.width, self.baseH * 4)

        for sprite, coords in array:
            self.fenetre.blit(sprite, (origin[0] + coords[0] * self.baseW, origin[1] - coords[1] * self.baseH))

        pygame.display.flip()

    def render_ui(self, dt, frames_per_update):
        # Hit message
        if self.game.player_status == Status.HIT and dt <= ((frames_per_update * 2) // 3):
            self.fenetre.blit(self.text, (((2 * self.game.width + 1) * self.baseW) // 2 - self.text.get_width() // 2, self.baseH * 2))

        # Hit proportion
        self.fenetre.blit(self.disp_hits, (((2 * self.game.width + 1) * self.baseW) - self.disp_hits.get_width(), 0))

        # Shields reloading
        for i in range(len(self.game.shields)):
            for j in range(self.game.shields[i]):
                self.fenetre.blit(self.to_blit[2 - i], (j * self.baseW, i * self.baseH))

    def prepare_rendering(self, frames_per_update, dt):
        render_list = []

        dt = self.inverse_dt(dt, frames_per_update)

        # Bullets
        for x, dir in self.bullet_list:
            render_list += [(self.bullet, (x - dir * dt / frames_per_update, 0))]

        # Frog
        perso_coords = (0, self.new_jump - self.jump_diff * dt / frames_per_update)
        render_list += [(self.perso, perso_coords)]

        # Shields
        for i in range(len(self.game.shields)):
            if self.game.shields[i] == 0:
                render_list += [(self.to_blit[i], perso_coords)]
                break

        self.render_ui(dt, frames_per_update)
        self.render(render_list)

    def inverse_dt(self, dt, frames_per_update):
        dt = frames_per_update - dt
        return dt

    def update(self, choose_action):
        old_jump = self.game.is_jumping

        state = game_to_state(self.game)
        chosen_action = choose_action(state)
        self.game.tick(chosen_action)

        self.new_jump = self.game.is_jumping
        self.jump_diff = self.new_jump - old_jump

        self.bullet_list = []
        for i in self.game.bullets:
            self.bullet_list += [(i[0], i[1])]
        for i in self.game.deadbullets:
            self.bullet_list += [(i[0], i[1])]

        proportion = (floor(100000 * self.game.nb_hit / self.game.shot_bullets) / 100) if self.game.shot_bullets > 0 else 0
        message = str(proportion) + "‰"
        self.disp_hits = self.font.render(message, True, (255, 255, 255))


def start_simulation(choose_action, frames_per_update = 10, game=Game(0.33, 5)):
    """
    
    :param choose_action: function, takes one parameter state, returns an Actions 
    :param frames_per_update: 
    :param game: 
    :return: 
    """
    continuer = 1
    t = 0
    game_ui = UI(game)
    while continuer:
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = 0

        game_ui.fenetre.fill((0, 0, 0))

        dt = t % frames_per_update

        if dt == 0:
            game_ui.update(choose_action)

        game_ui.prepare_rendering(frames_per_update, dt)

        pygame.time.Clock().tick(60)
        t += 1
