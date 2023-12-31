import pygame as pg
import math
from queue import PriorityQueue
from collections import deque

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
        self.death = False
        self.angle = 0
        self.health = 10
        self.vector = pg.Vector2()
        self.speed = 1
    
    def zombieCol(self, zombies):
        for zombie in zombies:
            #print((self.X <= zombie[0]+ZSIZE and self.X >= zombie[0]) or (self.X+PSIZE >= zombie[0] and self.X+PSIZE <= zombie[0]+ZSIZE)) and ((self.Y <= zombie[1]+ZSIZE and self.Y >= zombie[1]) or (self.Y+PSIZE >= zombie[1] and self.Y+PSIZE<=zombie[1]+ZSIZE))
            if ((self.X <= zombie[0]+ZSIZE and self.X >= zombie[0]) or (self.X+PSIZE >= zombie[0] and self.X+PSIZE <= zombie[0]+ZSIZE)) and ((self.Y <= zombie[1]+ZSIZE and self.Y >= zombie[1]) or (self.Y+PSIZE >= zombie[1] and self.Y+PSIZE<=zombie[1]+ZSIZE)):
                self.health -= 1
                #print('s')
            
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
        self.zombieCol(zombies)
        if self.health == 0:
            self.death = True
        #print(self.health)
        

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
        self.move = -1
    

    def bulletCol(self, bullets):
        for b in bullets:
            if ((self.X <= b[0]+TSIZE and self.X >= b[0]) or (self.X+PSIZE >= b[0] and self.X+PSIZE <= b[0]+TSIZE)) and ((self.Y <= b[1]+TSIZE and self.Y >= b[1]) or (self.Y+PSIZE >= b[1] and self.Y+PSIZE<=b[1]+TSIZE)):
                self.health -= 1

    def nestorandom(self, start, end, min):
        #print(end)
        q = PriorityQueue(605)
        visited = [0 for i in range(605)]
        DifX = end[0] - start[0]
        DifY = end[1] - start[1]
        q.put((DifX + DifY, DifX + DifY, 0, start[0] + TX * start[1]))
        while not q.empty():
            path, to, until, tile = q.get()
            #print(path)
            #print (tile)
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
                #print(tileX, tileY, visited[tileX + tileY * TX], self.map[tileX + tileY * TX] == 10)
                #print(tileX, tileY)
                if tileX >= 0 and tileX < TX and tileY >= 0 and tileY < TY and not visited[tileX + tileY * TX] and self.map[tileX + tileY * TX] == 10:
                    DifX = end[0] - tileX
                    DifY = end[1] - tileY
                    q.put((DifX + DifY + until + 1, DifX + DifY, until + 1, tileX + tileY * TX))
                tileX -= gridX[i]
                tileY -= gridY[i]
        return min

    def bfs(self, start, end):
        q = deque()
        visited = [0 for i in range(600)]
        path = {}
        q.append(list(start))
        visited[start[0] + start[1] * TX]
        while len(q)>0:
            pos = q.popleft()
            for i in range(4):
                pos[0] += gridX[i]
                pos[1] += gridY[i]

                if pos[0] < TX and pos[0] >= 0 and pos[1] < TY and pos[1] >= 0 and not visited[pos[0]+TX*pos[1]] and self.map[pos[0]+TX*pos[1]] == 10:
                    visited[pos[0]+TX*pos[1]] = 1
                    q.append(list(pos))
                    pos1 = pos.copy()
                    pos[0] -= gridX[i]
                    pos[1] -= gridY[i]
                    path[tuple(pos1)] = pos
                else:
                    pos[0] -= gridX[i]
                    pos[1] -= gridY[i]

        x = end
        while path[tuple(x)] != list(start):
            x = path[tuple(x)] 
        return x


    def update(self, players = None, bullets = None):
        #print("zombie", self.X, self.Y)
        if bullets == None: bullets = []
        if players == None: players = []
        #print(self.X // TSIZE, self.Y // TSIZE, (self.X + ZSIZE) // TSIZE, (self.Y + ZSIZE) // TSIZE)
        if (self.X // TSIZE == (self.X + ZSIZE) // TSIZE) and (self.Y // TSIZE == (self.Y + ZSIZE) // TSIZE):
            dist = {}
            for player in players:
                d = math.sqrt((player[0] // TSIZE -self.X // TSIZE)**2+(player[1] // TSIZE-self.Y // TSIZE)**2)
                dist[d] = (player[0] // TSIZE, player[1] // TSIZE)


            pos = self.bfs((self.X // TSIZE, self.Y // TSIZE), dist[min(dist)])
            for i in range(4):
                if pos[0] == (self.X // TSIZE) + gridX[i] and pos[1] == self.Y // TSIZE + gridY[i]:
                    self.move = i


        if self.move != -1:
            self.X += gridX[self.move] * self.Vel
            self.X = max(0, self.X)
            self.Y += gridY[self.move] * self.Vel
            self.Y = max(0, self.Y)
        if self.move == 0:
            self.angle = 0
        elif self.move == 1:
            self.angle = math.pi / 2
        elif self.move == 2:
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
    
