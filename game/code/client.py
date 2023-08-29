from networking import *
import math
import pygame as pg
pg.init()


class GameClient(Client):
    def __init__(self):
        super().__init__()
        self.display = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen = pg.Surface((WIDTH//2, HEIGHT//2))
        pg.display.set_caption('Zombiemania')
        self.clock = pg.time.Clock()
        self.spritesheet = pg.image.load(FOLDER/'assets'/'spritesheet.png').convert(self.screen)
        self.spritesheet.set_colorkey((0, 0, 0))
        self.song = pg.mixer.Sound(FOLDER/'assets'/'song.mp3')
        self.song.play(loops=9999)

        self.username = None
        self.usernameRect = pg.Rect(WIDTH//2*0.2, HEIGHT//2*0.4, WIDTH//2*0.6, HEIGHT//2*0.2)
        self.usernameFont = pg.font.SysFont('calibri', int(HEIGHT//2*0.2-10))
        self.usernameText = ''
        self.usernameEnter = pg.font.SysFont('calibri', int(HEIGHT//2*0.2-30)).render('Enter username:', False, (50, 50, 50))

        self.sendPos = True

        self.mapImage = pg.Surface((WIDTH//2, HEIGHT//2))
        for n, i in enumerate(MAP):
            y = n//MAP_SIZE[0]*TSIZE
            x = n%MAP_SIZE[0]*TSIZE
            self.mapImage.blit(self.getSprite(i), (x, y))
        
        self.images = [self.getSprite(i) for i in range(5)]

        self.players = [] #(x, y, angle, health, username)
        self.zombies = [] #(x, y, angle)
        self.bullets = [] #(x, y, angle)

        self.run()


    def getSprite(self, i):
        y = i//10
        x = i%10
        return self.spritesheet.subsurface((x*TSIZE, y*TSIZE, TSIZE, TSIZE))

    def rotSprite(self, image, pos, angle):
        image = pg.transform.rotate(image, math.degrees(angle))
        rect = image.get_rect(center=(pos[0]+image.get_width()//2, pos[1]+image.get_height()//2))
        return image, rect


    def draw(self):
        self.screen.fill('white')

        if not self.username:
            self.screen.blit(self.usernameEnter, (self.usernameRect.x, self.usernameRect.y-self.usernameEnter.get_height()-5))
            pg.draw.rect(self.screen, (0, 100, 0), self.usernameRect, border_radius=3)
            self.screen.blit(self.usernameFont.render(self.usernameText, False, (0, 0, 0)),
                              (self.usernameRect.x+5, self.usernameRect.y+5))
        else:
            self.screen.blit(self.mapImage, (0, 0))

            for p in self.players:
                self.screen.blit(self.images[0], (p[0], p[1]))

        self.display.blit(pg.transform.scale2x(self.screen), (0, 0))
        pg.display.flip()

    
    def run(self):
        self.running = True
        while self.running:
            if self.close: self.running = False
            mousePos = tuple(x//2 for x in pg.mouse.get_pos())
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if not self.username:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_BACKSPACE:
                            self.usernameText = self.usernameText[:-1]
                        elif event.key == pg.K_RETURN:
                            if self.usernameText:
                                send(self.s, {'username':self.usernameText})
                        elif len(self.usernameText)<=8 and event.unicode in 'qwertyuiopasdfghjklzxcvbnm.,_123456789':
                            self.usernameText += event.unicode
                else:
                    self.sendPos = False
                    if event.type == pg.KEYDOWN:
                        if event.unicode in 'wasd':
                            send(self.s, {'move':event.unicode+'d'})
                    if event.type == pg.KEYUP:
                        if event.unicode in 'wasd':
                            send(self.s, {'move':event.unicode+'u'})
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        send(self.s, {'click':mousePos})
                             
                    send(self.s, {'mouseP':mousePos})

            if self.username:
                if self.sendPos:
                    send(self.s, {'mouseP':mousePos})
                else:
                    self.sendPos = True

            


            for eventDict in self.eventList:
                if 'username' in eventDict.keys():
                    self.username = eventDict['username']
                if self.username:
                    if 'players' in eventDict.keys():
                        self.players = eventDict['players']

                self.eventList.remove(eventDict)

            self.draw()
            self.clock.tick(FPS)
        
        pg.quit()
        self.s.close()


if __name__ == '__main__':
    GameClient()