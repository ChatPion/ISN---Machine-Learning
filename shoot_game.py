# Règles :
# d'abord regénérer un bouclier 
# puis avancée des tirs
# puis créer ou pas une balle (de chaque côté)
# puis sauter/rien faire
# puis tomber de 1
# enfin prendre des dégâts

# boucliers : vaut temps de rechargement (0 si disponible)

from enum import Enum
import random as rand

class Actions(Enum):
    STAND = 0
    JUMP = 1

class Status(Enum):
    NOTHING = 0
    HIT = 1
    DOUBLE_HIT = 2 # Si le joueur sans bouclier reçoit une balle de chaque côté
    SHIELD_HIT = 3
    DODGED = 4 # Si le joueur est en l'air avec une balle en dessous.

class Game:

    def __init__(self, probability, width, shields=None):
        """
        :param probability: bullets apparition probability in [0; 1]
        :param width: bullet spawn distance
        :param shields: array with shields' cooldown time ([0] : external shield, [1] : internal  shield)
        """
        if shields is None:
            shields = [6, 4]

        self.probability = probability
        self.width = width
        self.bullets = []  # Les balles qui vont vers le joueur
        self.deadbullets = []  # Les balles qui ont déjà dépassé le joueur
        self.is_jumping = 0  # L'altitude du joueur (0, 1 ou 2)
        self.time = 0
        self.shot_bullets = 0 # Le nombre de balles tirées depuis le début de la partie
        self.nb_hit = 0  # Le nombre de balles reçues sans bouclier depuis le début de la partie
        self.shields_cooldown = shields
        self.shields = [0 for i in shields]
        self.player_status = Status.NOTHING

    def shoot(self, position, direction): # Fait apparaître une balle
        self.bullets.append([position, direction])

    def jump(self): # Fait sauter le joueur
        if self.is_jumping == 0:
            self.is_jumping = 3

    def move_bullets(self): # Fait avancer les balles
        """
        :return to_kill: Number of bullets that reached 0 
        """
        to_kill = 0 # Le nombre de balles atteignant 0 après déplacement
        to_delete = 0 # Le nombre de balles sortant de l'écran après déplacement
        for i in range(len(self.bullets)):
            self.bullets[i][0] += self.bullets[i][1] # Incrémente ou décrémente de 1 la position
            if self.bullets[i][0] == 0:
                to_kill += 1
        for i in range(len(self.deadbullets)):
            self.deadbullets[i][0] += self.deadbullets[i][1]
            if abs(self.deadbullets[i][0]) > self.width:
                to_delete += 1
        for i in range(to_kill): 
            self.deadbullets.append([0, self.bullets[0][1]]) # Transfère les balles de bullets en 0 (indices [0; to_kill[) à la fin de deadbullets
            del self.bullets[0] # Supprime les balles en 0 de bullets
        for i in range(to_delete):
            del self.deadbullets[0] # Supprime les balles sortant de l'écran de deadbullets (indices [0; to_delete[)

        return to_kill

    def take_dmg(self): # Appelée à chaque fois qu'une balle arrive en 0
        """
        :return: True if hit without a shield, False if other
        """
        if self.player_status == Status.HIT:
            self.player_status = Status.DOUBLE_HIT
            return True
        
        if self.is_jumping > 0:
            self.player_status = Status.DODGED
            return False

        for i in range(len(self.shields)):
            if self.shields[i] == 0: # S'il a au moins un bouclier prêt (valeur = 0)
                self.shields[i] = self.shields_cooldown[i] # Désactive le bouclier
                self.player_status = Status.SHIELD_HIT
                return False
        
        self.player_status = Status.HIT
        self.nb_hit += 1
        return True

    def fall(self):
        if self.is_jumping > 0:
            self.is_jumping -= 1

    def regen_shields(self):
        for i in reversed(range(0, len(self.shields))): # Regénère en priorité le bouclier intérieur (indice 1)
            if self.shields[i] != 0:
                self.shields[i] = max(0, self.shields[i] - 1)
                break

    def generate_bullets(self):
        if rand.uniform(0, 1) < self.probability:
            self.shoot(self.width, -1)
        if rand.uniform(0, 1) < self.probability:
            self.shoot(-self.width, 1)

    def tick(self, action):
        """
        :param action: STAND or JUMP 
        """
        
        self.player_status = Status.NOTHING
        self.regen_shields()

        bullets_at_center = self.move_bullets()
        self.shot_bullets += bullets_at_center
        self.generate_bullets()
        
        if action == Actions.JUMP:
            self.jump()
        self.fall()

        for i in range(bullets_at_center):
            self.take_dmg()
            
        self.time += 1

    def reset(self):
        self.bullets = []
        self.deadbullets = []
        self.is_jumping = 0
        self.time = 0
        self.shot_bullets = 0
        self.nb_hit = 0
        self.shields = [0 for i in self.shields]
        self.player_status = Status.NOTHING

