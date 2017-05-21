# Règles :
# d'abord sauter/rien faire
# puis avancée des tirs
# puis créer ou pas une balle
# puis tomber de 1
# boucliers : vaut 0 quand disponible

from enum import Enum
import random as rand

class Actions(Enum):
    STAND = 0
    JUMP = 1

class Status(Enum):
    NOTHING = 0
    HIT = 1
    SHIELD_HIT = 2
    DODGED = 3

class Game:

    STAND = 0
    JUMP = 1
    HIT = 2
    UNHARMED = 3

    def __init__(self, probability, width, shields=None):
        """
        :param probability: bullets apparition probability in ]0; 1]
        :param width: bullet spawn distance
        :param shields: array with shields' cooldown time ([0] : ext shield)
        """
        if shields is None:
            shields = [6, 4]

        self.probability = probability
        self.width = width
        self.bullets = []
        self.deadbullets = []
        self.is_jumping = 0
        self.time = 0
        self.shot_bullets = 0
        self.nb_hit = 0
        self.shields_cooldown = shields 
        self.shields = [0 for i in shields] 
        self.player_status = Status.NOTHING

    def shoot(self, position, direction):
        self.bullets.append([position, direction])

    def jump(self):
        if self.is_jumping == 0:
            self.is_jumping = 3

    def move_bullets(self):
        """
        
        :return: True if a bullet reached 0 
        """
        to_kill = 0
        to_delete = 0
        for i in range(len(self.bullets)):
            self.bullets[i][0] += self.bullets[i][1]
            if self.bullets[i][0] == 0:
                to_kill += 1
        for i in range(len(self.deadbullets)):
            self.deadbullets[i][0] += self.deadbullets[i][1]
            if abs(self.deadbullets[i][0]) > self.width:
                to_delete += 1
        for i in range(to_kill):
            self.deadbullets.append([0, self.bullets[0][1]])
            del self.bullets[0]
        for i in range(to_delete):
            del self.deadbullets[0]

        return to_kill

    def take_dmg(self):
        if self.is_jumping > 0:
            self.player_status = Status.DODGED
            return False

        for i in range(len(self.shields)):
            if self.shields[i] == 0:
                self.shields[i] = self.shields_cooldown[i]
                self.player_status = Status.SHIELD_HIT
                return False

        self.player_status = Status.HIT
        self.nb_hit += 1
        return True

    def fall(self):
        if self.is_jumping > 0:
            self.is_jumping -= 1

    def regen_shields(self):
        for i in range(len(self.shields) - 1, -1, -1):
            if self.shields[i] != 0:
                self.shields[i] = max(0, self.shields[i] - 1)
                break

    def generate_bullets(self):
        nb = 0
        if rand.uniform(0, 1) < self.probability:
            self.shoot(self.width, -1)
            nb += 1
        if rand.uniform(0, 1) < self.probability:
            self.shoot(-self.width, 1)
            nb += 1
        return nb

    def tick(self, action):
        """
        
        :param action: STAND or JUMP 
        :return: 0 : HIT, UNHARMED
        """
        
        self.player_status = Status.NOTHING
        self.regen_shields()

        bullets_at_center = self.move_bullets()
        self.shot_bullets += self.generate_bullets()
        
        if action == Actions.JUMP:
            self.jump()
        self.fall()

        for i in range(bullets_at_center):
            self.take_dmg()
            
        self.time += 1

