# Règles :
# d'abord sauter/rien faire
# puis avancée des tirs

class Game:
    
    STAND = 0
    JUMP = 1
    
    def __init__(self, frequency, width, vision):
        self.frequency = frequency
        self.width = width
        self.vision = vision
        self.bullets = []
        self.deadbullets = []
        self.is_jumping = 0
        self.time = 0
    
    
    def shoot(self, position, direction):
        self.bullets.append([position, direction])
    
    def jump(self):
        self.is_jumping = 2
    
    def tick(self, action):
        if action == Game.JUMP:
            self.jump()
        
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
        
        if self.is_jumping > 0:
            self.is_jumping -= 1
        
        if self.time % (1/self.frequency) == 0:
            self.shoot(self.width, -1)
        
        self.time += 1
        
        if to_kill != 0:
            return self.is_shot()
        else:
            return 1
            
    def is_shot(self):
        if self.is_jumping == 0:
            return 0
        else:
            return 2
            