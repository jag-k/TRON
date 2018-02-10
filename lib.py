import json
from pprint import pprint

from model_converter import *
import pygame

import os

pygame.init()

# CONSTANTS


K_UP = pygame.K_UP
K_DOWN = pygame.K_DOWN
K_RIGHT = pygame.K_RIGHT
K_LEFT = pygame.K_LEFT

W = pygame.K_w
A = pygame.K_a
S = pygame.K_s
D = pygame.K_d


D_UP = (0, -1)
D_DOWN = (0, 1)
D_RIGHT = (1, 0)
D_LEFT = (-1, 0)
D_CENTER = (0, 0)


UP = "up"
DOWN = "down"
RIGHT = "right"
LEFT = "left"
CENTER = "center"


CONVERT_DIRECTIONAL = {
    UP: D_UP,
    DOWN: D_DOWN,
    LEFT: D_LEFT,
    RIGHT: D_RIGHT,
    CENTER: D_CENTER,

    D_UP: UP,
    D_DOWN: DOWN,
    D_LEFT: LEFT,
    D_RIGHT: RIGHT,
    D_CENTER: CENTER
}


REVERSE_DIRECTIONAL = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
    CENTER: CENTER,

    D_UP: D_DOWN,
    D_DOWN: D_UP,
    D_LEFT: D_RIGHT,
    D_RIGHT: D_LEFT,
    D_CENTER: D_CENTER,
}


STORE_COEFFICIENT = 1


# SETTINGS

game_difficulty = 'normal'

models = {
    "players": dict(
        (i.split('_player.model')[0], Model(i))
        for i in filter(lambda x: x.endswith('player.model'),
                        os.listdir('data/models'))
    ),

    "tracks": dict(
        (i.split('_track.model')[0], Model(i))
        for i in filter(lambda x: x.endswith('track.model'),
                        os.listdir('data/models'))
    )
}

pprint(models)


def update_settings():
    settings = json.load(open('./data/settings.json'))
    return settings


settings = update_settings()
# pprint(settings)


def save_setting():
    json.dump(settings, open('./data/settings.json', 'w'), indent=2)
    update_settings()


# ANOTHER METHODS AND CLASSES

def edit_pos(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return x1+x2, y1+y2


class Store:
    def __init__(self, player):
        self.file = './data/store.json'
        self.player = player
        self.count = 0
        self.high_store = self.get_store[player.name] if player.name in self.get_store else 0

    def __str__(self):
        return "%s: %d (HS: %d)" % (self.player.name, self.count, self.high_store)

    @property
    def get_store(self):
        return json.load(open(self.file))

    def save_store(self):
        result = self.get_store
        result[self.player.name] = self.high_store
        json.dump(result, open(self.file, 'w'), indent=2)

    def add_points(self, count):
        self.count += count*STORE_COEFFICIENT
        if self.count > self.high_store:
            self.high_store = self.count
        return self.save_store


class EmptyCell:
    def __init__(self, x, y, board):
        self.x, self.y = x, y
        self.board = board

    # def __repr__(self):
    #     return "<%s object at position %s>" % (type(self).__name__, self.pos)

    def __repr__(self):
        return "%s%s" % (type(self).__name__[0], self.pos)

    def __str__(self):
        return "E"

    @property
    def pos(self):
        return self.x, self.y

    def delete(self):
        self.board.board[self.x][self.y] = EmptyCell(self.x, self.y, self.board)


class Player(EmptyCell):
    def __init__(self, x, y, direction, board, name):
        super().__init__(x, y, board)
        self.start = self.startx, self.starty = x, y
        self.old_d = CENTER
        self.d = direction
        self.live = True
        self.name = name
        self.tracks = []
        self.store = Store(self)
        self.color = pygame.Color(settings['players_color'][name] if name in settings['players_color']
                                  else settings['players_color']['default'])

    def __str__(self):
        return "P"

    def next(self):
        board = self.board.board
        if self in self.board.flat:
            x, y = self.x, self.y

            nextx, nexty = edit_pos(self.pos, CONVERT_DIRECTIONAL[self.d])

            if type(board[nextx][nexty]) is EmptyCell:
                track = Track(x, y, self.board, self, (self.d, REVERSE_DIRECTIONAL[self.old_d]))
                board[self.x][self.y] = track
                self.tracks.append(track)
                self.edit_dir(self.d)
                self.store.add_points(settings['points_price'][game_difficulty])

                self.x, self.y = nextx, nexty
                board[self.x][self.y] = self
            else:
                self.store.save_store()
                self.delete()
                print(self.store)

        p = ''
        for i in Board.rotate(board):
            p += ' '.join(str(j) for j in i)+'\n'
        print(p)

    def render(self, surface, bg=None):
        m = models['players'][self.d[0]]
        m.render(surface, self.board.rect(self.pos), self.color, bg)

    def edit_dir(self, dir):
        if self.d != REVERSE_DIRECTIONAL[dir]:
            self.old_d = self.d
            self.d = dir

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_UP:
                self.edit_dir(UP)
            elif event.key == K_DOWN:
                self.edit_dir(DOWN)
            elif event.key == K_LEFT:
                self.edit_dir(LEFT)
            elif event.key == K_RIGHT:
                self.edit_dir(RIGHT)


class Track(EmptyCell):
    def __init__(self, x, y, board, player=Player, dirs=(CENTER, UP)):
        super().__init__(x, y, board)
        self.player = player
        self.start_dir, self.end_dir = dirs

    def __str__(self):
        return "T"

    def render(self, surface, bg=None):
        rect = self.board.rect(self.x, self.y)
        convert = {
            CENTER: rect.center,
            UP: (rect.centerx, rect.top),
            DOWN: (rect.centerx, rect.bottom),
            RIGHT: (rect.right, rect.centery),
            LEFT: (rect.left, rect.centery)}

        # draw_line(self.start_dir)
        # draw_line(self.end_dir)

        m = models['tracks'][''.join(sorted([self.start_dir[0], self.end_dir[0]]))]
        m.render(surface, self.board.rect(self.pos), self.player.color, bg)
        # pygame.draw.circle(surface, (255, 0, 0), rect.center, rect.w//2)

    def update(self, *args):
        if self.player not in self.board.flat:
            self.board.board[self.x][self.y] = EmptyCell(self.x, self.y, self.board)


class Board:
    def __init__(self, width=100, height=100, cell_size=30, *start_pos):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.top = 10
        self.left = 10
        self.start_pos = start_pos
        self.show_grid = True
        name = map(str, settings['players'])
        self.board = [[Player(x, y, RIGHT, self, next(name)) if (x, y) in start_pos else EmptyCell(x, y, self)
                       for y in range(height)]
                      for x in range(width)]

    def set_board(self, board):
        self.board = board

    @property
    def get_size(self):
        return self.width * self.cell_size + self.left * 2, self.height * self.cell_size + self.top * 2

    @property
    def flat(self):
        return list(j for i in self.board for j in i)

    @property
    def get_players(self):
        return [j for i in self.board for j in i if type(j) is Player]

    @staticmethod
    def rotate(array, rotate=1):
        res = array
        for i in range(rotate):
            res = list(zip(*res[::-1]))
        return res

    def __iter__(self):
        res = []
        for i in self.board:
            res += i
        return res

    def set_view(self, left=None, top=None, cell_size=None):
        self.left = left if left is not None else self.left
        self.top = top if top is not None else self.top
        self.cell_size = cell_size if cell_size is not None else self.cell_size

    def render(self, surface, bg=None):
        for x in range(self.width):
            for y in range(self.height):
                render = getattr(self.board[x][y], "render", None)
                if callable(render):
                    self.board[x][y].render(surface, bg)
                if self.show_grid:
                    pygame.draw.rect(surface, (255, 255, 255), self.rect(x, y), 1)

    def rect(self, x, y=None):
        if y is None:
            x, y = x
        return pygame.Rect(self.left + (x * self.cell_size), self.top + (y * self.cell_size),
                           self.cell_size, self.cell_size)

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self.show_grid = not self.show_grid
        for i in filter(lambda x: type(x) == Player, self.flat):
            get_event = getattr(i, "get_event", None)
            if callable(get_event):
                i.get_event(event)

    def next_step(self):
        for p in self.get_players:
            p.next()

    def update(self, *args):
        for i in self.flat:
            update = getattr(i, "update", None)
            if callable(update):
                i.update(*args)
