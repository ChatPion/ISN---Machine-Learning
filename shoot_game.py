# Règles :
# d'abord sauter/rien faire
# puis avancée des tirs
# puis créer ou pas une balle
# puis tomber de 1

class Game:

    STAND = 0
    JUMP = 1

    def __init__(self, frequency, width, vision, shields):
        self.frequency = frequency
        self.width = width
        self.vision = vision
        self.bullets = []
        self.deadbullets = []
        self.is_jumping = 0
        self.time = 0
        self.shieldext = 0
        self.shieldint = 0
        if shields == 1:
            self.shieldext = 2 
            self.shieldint = 0
        elif shields == 2:
            self.shieldext = 4
            self.shieldint = 2

    def shoot(self, position, direction):
        self.bullets.append([position, direction])

    def jump(self):
        if self.is_jumping == 0:
            self.is_jumping = 2

    def move_bullets(self):
        to_kill = 0
        to_delete = 0
        for i in range (len(self.bullets)):
            self.bullets[i][0] += self.bullets[i][1]
            if self.bullets[i][0] == 0:
                to_kill += 1
        for i in range (len(self.deadbullets)):
            self.deadbullets[i][0] += self.deadbullets[i][1]
            if abs(self.deadbullets[i][0]) > self.width:
                to_delete += 1
        for i in range (to_kill):
            self.deadbullets.append([0, self.bullets[0][1]])
            del self.bullets[0]
        for i in range (to_delete):
            del self.deadbullets[0]

    def fall(self):
        if self.is_jumping > 0:
            self.is_jumping -= 1
            return 2
        else:
            return 0

    def tick(self, action):
        if action == Game.JUMP:
            self.jump()

        print(self.bullets, self.deadbullets)
        self.move_bullets()
        print(self.bullets, self.deadbullets)

        if self.time % (1/self.frequency) == 0:
            self.shoot(self.width, -1)

        self.time += 1

        if self.deadbullets != [] and self.deadbullets[len(self.deadbullets)-1][0] == 0:
            return self.fall()
        else:
            self.fall()
            return 1

game = Game (1/5, 5, 3, 0)
for i in range (15):
    print(game.tick(Game.STAND))




