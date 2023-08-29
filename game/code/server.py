from networking import *
import pygame as pg
from classes import *


class GameServer(Server):
    def __init__(self):
        super().__init__()
        self.clock = pg.time.Clock()

        self.state = 'waiting'

        self.dt = 1
        
        self.walls = []
        self.zombies = [Zombie(100, 100, (1, 1, 1), MAP)]

        for i, v in enumerate(MAP):
            if v == 11:
                y = i//MAP_SIZE[0]*TSIZE
                x = i%MAP_SIZE[0]*TSIZE
                self.walls.append((x, y))


        while True:

            #if len(self.players) >= 2 and self.state == 'waiting':
            #    self.state = 'starting'
            #elif self.state == 'starting':
            #    ...
            #    self.state = 'running'
            #elif (self.state == 'running' and len(self.players) < 2) or any([p.health<=0 for p in self.players.values()]):
            #    self.state = 'stopping'
            #elif self.state == 'stopping':
            #    if len(self.players) >= 2:
            #        self.state = 'starting'
            #    else:
            #        self.state = 'waiting'

            for eventDict in self.eventList:
                for username, playerInput in eventDict.items():
                    if 'move' in playerInput.keys():
                        if username in self.players.keys():
                            self.players[username].update(moves=playerInput['move'], walls=self.walls)
                    if 'mouseP' in playerInput.keys():
                        if username in self.players.keys():
                            self.players[username].update(mPos=playerInput['mouseP'], walls=self.walls)
                self.eventList.remove(eventDict)

            
            playersPos = []
            for p in list(self.players.values()).copy():
                playersPos.append((p.X, p.Y))

            for zombie in self.zombies:
                zombie.update(playersPos)
                

            players = []
            for u, p in self.players.items():
                players.append([p.X, p.Y, p.angle, p.health, u])

            zombies = []
            for z in self.zombies:
                zombies.append([z.X, z.Y, z.angle])

            self.broadcast({'players':players, 'zombies':zombies})

            self.clock.tick(FPS)


if __name__ == '__main__':
    GameServer()
