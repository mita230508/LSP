import socket
import json
from threading import Thread
from classes import Player, TSIZE
import random
from pathlib import Path


ADDR = ('127.0.0.1', 65432)
HEADER_SIZE = 60
FORMAT = 'ascii'
WIDTH, HEIGHT = 960, 640
FPS = 60
FOLDER = Path(__file__).parents[1]
MAP_SIZE = WIDTH//TSIZE//2, HEIGHT//TSIZE//2
with open(FOLDER/'assets'/'map.txt') as f:
    MAP = f.read()
    MAP = list(map(int, MAP.split(',')))


def send(s, msg):
    try:
        msgB = json.dumps(msg).encode(FORMAT)
        msgLenB = str(len(msgB)).encode(FORMAT).ljust(HEADER_SIZE, ' '.encode(FORMAT))
        s.sendall(msgLenB+msgB)
    except:
        pass

def recv(s):
    try:
        msgLen = int(s.recv(HEADER_SIZE).decode(FORMAT))
        msg = json.loads(s.recv(msgLen))
    except:
        return False
    return msg


class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(ADDR)
        self.eventList = []
        self.close = False

        Thread(target=self.recvThread).start()
        

    def recvThread(self):
        while True:
            msg = recv(self.s)
            if not msg:
                self.close = True
                break
            self.eventList.append(msg)


class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(ADDR)

        self.clients = []
        self.eventList = []
        self.players = {}

        Thread(target=self.acceptThread).start()
    

    def acceptThread(self):
        self.s.listen()
        while True:
            if len(self.clients) >= 2: continue
            conn, _ = self.s.accept()
            self.clients.append(conn)

            Thread(target=self.clientThread, args=(conn,)).start()


    def broadcast(self, msg):
        for client in self.clients:
            send(client, msg)


    def clientThread(self, conn):
        username = None
        while not username:
            x = recv(conn)
            if not x: 
                self.clients.remove(conn)
                conn.close()
                return 0
            x = list(x.items())[0][1]
            if x not in self.players:
                self.players[x] = Player(3 * 16 + 1, 15 * 16 + 1)
                username = x
                send(conn, {'username':x})
                break


        while True:
            msg = recv(conn)
            if not msg:
                self.clients.remove(conn)
                del self.players[username]
                conn.close()
                return 0
            self.eventList.append({username:msg})
