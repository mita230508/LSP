import pygame as pg
import math
from queue import PriorityQueue

WIDTH,  HEIGHT = 480, 320
TSIZE = 16
PSIZE = 14
ZSIZE = 10
BSIZE = 4
TX, TY = 30 , 20
gridX = (1, 0, -1, 0)
gridY = (0, 1, 0, -1)

class Player():
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.angle = 0
        self.health = 10
        self.vector = pg.Vector2()
        self.speed = 1
    
    def zombieCol(self, zombies):
        for zombie in zombies:
            if zombie[0] + ZSIZE > self.X and self.X >= zombie[0]:
                self.health -= zombie[2]
            elif zombie[0] < self.X + TSIZE and self.X <= zombie[0]:
                self.health -= zombie[2]
            elif zombie[1] + ZSIZE < self.Y + TSIZE and zombie[1] + ZSIZE > self.Y:
                self.health -= zombie[2]
            elif zombie[1] < self.Y + TSIZE and zombie[1] > self.Y:
                self.health -= zombie[2]

    def wallCol(self, walls, d):
        if d == 'h':
            for wall in walls:
                if ((self.X <= wall[0]+TSIZE and self.X >= wall[0]) or (self.X+PSIZE >= wall[0] and self.X+PSIZE <= wall[0]+TSIZE)) and ((self.Y <= wall[1]+TSIZE and self.Y >= wall[1]) or (self.Y+PSIZE >= wall[1] and self.Y+PSIZE<=wall[1]+TSIZE)):
                    if self.vector.x > 0:
                        self.X = wall[0] - PSIZE-1
                    elif self.vector.x < 0:
                        self.X = wall[0] + TSIZE+1

        elif d == 'v':
            for wall in walls:
                if ((self.X <= wall[0]+TSIZE and self.X >= wall[0]) or (self.X+PSIZE >= wall[0] and self.X+PSIZE <= wall[0]+TSIZE)) and ((self.Y <= wall[1]+TSIZE and self.Y >= wall[1]) or (self.Y+PSIZE >= wall[1] and self.Y+PSIZE<=wall[1]+TSIZE)):
                    if self.vector.y > 0:
                        self.Y = wall[1] - PSIZE-1
                    elif self.vector.y < 0:
                        self.Y = wall[1] + TSIZE+1

    def borderCheck(self):
        
        if self.X < 0:
            self.X = 0
        elif self.X + PSIZE > WIDTH:
            self.X = WIDTH - PSIZE
        if self.Y < 0:
            self.Y = 0
        elif self.Y + PSIZE > HEIGHT:
            self.Y = HEIGHT - PSIZE

    def updVel(self, l, walls):
        if self.vector.x>0:
            self.vector.x = 1
        elif self.vector.x<0:
            self.vector.x = -1
        if self.vector.y>0:
            self.vector.y = 1
        elif self.vector.y<0:
            self.vector.y = -1
        
        if l == 'wd':
            self.vector.y = -1
        elif l == 'sd':
            self.vector.y = 1
        if self.vector.y == -1 and l == 'wu':
            self.vector.y = 0
        elif self.vector.y == 1 and l == 'su':
            self.vector.y = 0
        if l == 'dd':
            self.vector.x = 1
        elif l == 'ad':
            self.vector.x = -1
        if self.vector.x == -1 and l == 'au':
            self.vector.x = 0
        elif self.vector.x == 1 and l == 'du':
            self.vector.x = 0

        
        self.X += self.vector.x*self.speed
        self.wallCol(walls, 'h')
        self.Y += self.vector.y*self.speed
        self.wallCol(walls, 'v')
        
    
    def update(self, moves = None, mPos = None, walls = None, zombies = None):
        if moves==None: moves = 'x'
        if mPos==None:mPos=[]
        if zombies==None:zombies=[]
        if mPos:
            self.angle = math.atan2(mPos[1] - self.Y, mPos[0] - self.X)
        self.updVel(moves, walls)
        self.borderCheck()
        if zombies:
            self.zombieCol(zombies)

class Zombie():
    def __init__(self, X, Y, types, map):
        self.X = X
        self.Y = Y
        self.Tile = X % TX + (Y % TY) * TY
        self.Vel = types[0]
        self.health = types[1]
        self.map = map
        self.timer = 0
        self.Strength = types[2]
        self.angle = 0
    
    def playerCol(self, players):
        for username, p in players.items():
            if players[username]:
                if ((self.X <= p[0]+TSIZE and self.X >= p[0]) or (self.X+PSIZE >= p[0] and self.X+PSIZE <= p[0]+TSIZE)) and ((self.Y <= p[1]+TSIZE and self.Y >= p[1]) or (self.Y+PSIZE >= p[1] and self.Y+PSIZE<=p[1]+TSIZE)):
                    players[username].heatlh -= 1

    def bulletCol(self, bullets):
        for b in bullets:
            if ((self.X <= b[0]+TSIZE and self.X >= b[0]) or (self.X+PSIZE >= b[0] and self.X+PSIZE <= b[0]+TSIZE)) and ((self.Y <= b[1]+TSIZE and self.Y >= b[1]) or (self.Y+PSIZE >= b[1] and self.Y+PSIZE<=b[1]+TSIZE)):
                self.health -= 1

    def findPath(self, start, end, min):
        q = PriorityQueue(605)
        visited = [0 for i in range(605)]
        DifX = abs(end[0] - start[0])
        DifY = abs(end[1] - start[1])
        q._put((DifX + DifY, DifX + DifY, 0, start[0] + TX * start[1]))
        while not q.empty():
            path, to, until, tile = q._get()
            if to == 0:
                if min > until:
                    min = until
                break
            visited[tile] = True
            tileX = tile % TX
            tileY = tile // TX
            for i in range(4):
                tileX += gridX[i]
                tileY += gridY[i]
                if tileX >= 0 and tileX < TX and tileY >= 0 and tileY < TY and not visited[tileX + tileY * TX] and self.map[tileX + tileY * TX] == 10:
                    DifX = abs(end[0] - tileX)
                    DifY = abs(end[1] - tileY)
                    q._put((DifX + DifY + until + 1, DifX + DifY, until + 1, tileX + tileY * TX))
                tileX -= gridX[i]
                tileY -= gridY[i]
        return min

    def update(self, map, playersPos = None, bullets = None):
        if bullets == None: bullets = []
        if (self.X % TX < TSIZE - ZSIZE) and (self.Y % TY < TSIZE - ZSIZE):
            startX = self.X // TX
            startY = self.Y // TY
            min = 605
            move = 0
            for player in playersPos:
                for i in range(4):
                    startX += gridX[i]
                    startY += gridY[i]
                    if startX < TX and startX >= 0 and startY < TY and startY >= 0 and self.map[startX + startY * TX]:
                        a = self.findPath((startX, startY), (player[0] % TX, player[1] % TY), map, min)
                        if a < min:
                            move = i
                            min = a
                    startX -= gridX[i]
                    startY -= gridY[i]
        self.X += gridX[move] * self.Vel
        self.Y += gridY[move] * self.Vel
        if (move == 0):
            self.angle = 0
        elif (move == 1):
            self.angle = math.pi / 2
        elif move == 2:
            self.angle = math.pi
        else:
            self.angle = 3 * math.pi / 2
        self.bulletCol(bullets)

class Wall():
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

class Bullet():
    def __init__(self, X, Y, angle):
        self.X = X
        self.Y = Y
        self.angle = angle
        self.Vel = 15
        self.VelX = math.cos(angle) * self.Vel
        self.VelY = math.sin(angle) * self.Vel
        self.remove = False

    def zombieCol(self, zombies):
        for z in zombies:
            if ((self.X <= z[0]+TSIZE and self.X >= z[0]) or (self.X+PSIZE >= z[0] and self.X+PSIZE <= z[0]+TSIZE)) and ((self.Y <= z[1]+TSIZE and self.Y >= z[1]) or (self.Y+PSIZE >= z[1] and self.Y+PSIZE<=z[1]+TSIZE)):
                self.remove = True

    def wallCol(self, walls):
        for wall in walls:
            if ((self.X <= wall[0]+TSIZE and self.X >= wall[0]) or (self.X+PSIZE >= wall[0] and self.X+PSIZE <= wall[0]+TSIZE)) and ((self.Y <= wall[1]+TSIZE and self.Y >= wall[1]) or (self.Y+PSIZE >= wall[1] and self.Y+PSIZE<=wall[1]+TSIZE)):
                self.remove = True

    def borderCheck(self):
        if self.X < 0:
            self.remove = True
        elif self.X + BSIZE > WIDTH:
            self.remove = True
        elif self.Y < 0:
            self.remove = True
        elif self.Y + BSIZE > HEIGHT:
            self.remove = True

    def update(self, walls = None, zombies = None):
        self.X += self.VelX
        self.Y += self.VelY
        self.borderCheck()
        self.wallCol(walls)
        self.zombieCol(zombies)
    