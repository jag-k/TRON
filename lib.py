import json
import sys
from GUI import *
from print_debug import print_debug, pprint_debug
from model_converter import *
import os
import pygame
pygame.init()


# SETTINGS

game_difficulty = 'normal'


settings = {}


def update_settings():
    global settings
    settings = json.load(open('./data/settings.json'))
    return settings


def save_setting():
    json.dump(settings, open('./data/settings.json', 'w'), indent=2)
    return update_settings()


update_settings()


# CONSTANTS AND VARIABLES

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
pygame.display.set_mode((1, 1))
raw_logo = pygame.image.load(os.path.join('data', 'images', settings['textures']['logo'])).convert_alpha()
pygame.display.quit()
LOGO_IMAGE: pygame.Surface = pygame.transform.scale(raw_logo, (raw_logo.get_width()*3, raw_logo.get_height()*3))

all_boards = []
music = pygame.mixer.music
join = os.path.join


# MODELS

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

pprint_debug(models)

# METHODS

def edit_pos(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return x1+x2, y1+y2


def terminate():
    for i in all_boards:
        i.delete()
    pygame.quit()
    sys.exit()


def init_music():
    if settings['music']['play']:
        music.load(join('data', 'music', settings['music']['file']))
    music.play(settings['music']['loops'], settings['music']['start'])
    music.set_volume(0.0)
    pygame.time.set_timer(26, 350)


def music_volume_event(event, coef=0.01):
    if event.type == 26 and int(music.get_volume() * 100) < settings['music']['max_volume'] + 1:
        volume = music.get_volume()
        music.set_volume(volume + coef)
        print_debug("Volume: %d" % (volume * 100))


def create_board():
    data = settings['textures']['board']
    b = Board(30, 30, settings['players_name'], 15, **data['padding'])
    b.show_border(settings['textures']['game']['show_border'])
    b.show_grid(settings['textures']['game']['show_grid'])
    return b


try:
    from tkinter import colorchooser

    def palette(color=None, **option):
        if type(color) is pygame.Color:
            color = color.r, color.g, color.b
        c = colorchooser.askcolor(color, **option)[1]
        return pygame.Color(c), c
except ImportError:
    print("\x1b[31;1mPlease, install Tkinter (pip install python3-tk)\x1b[0m")

    def pallete(color=None, **option):
        return pygame.Color, color

# CLASSES


class Store:
    def __init__(self, player):
        self.file = './data/store.json'
        self.player = player
        self.count = 0
        self.high_store = self.get_store[player.name] if player.name in self.get_store else 0

    def __str__(self):
        return "%s: %d (HS: %d)" % (self.player.name, self.count, self.high_store)

    def __int__(self):
        return self.count

    @property
    def get_hs(self):
        return self.high_store

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

    def __repr__(self):
        return "%s%s" % (type(self).__name__[0], self.pos)

    def __str__(self):
        return "E"

    @property
    def pos(self):
        return self.x, self.y

    def delete(self, full=False):
        self.board.board[self.x][self.y] = EmptyCell(self.x, self.y, self.board) if not full else 0


class Player(EmptyCell):
    def __init__(self, x, y, board, name):
        super().__init__(x, y, board)
        self.start = self.startx, self.starty = x, y
        self.old_d = CENTER
        self.d = settings['players'][name]['direction']
        self.name = name
        self.control = settings['players'][name]['control']
        self.tracks = []
        self.step = True
        self.next_count = 0
        self.render_count = -1
        self.store = Store(self)
        self.color = pygame.Color(settings['players'][name]['color']
                                  if name in settings['players_name'] else
                                  settings['players_color']['default']['color'])
        print_debug("%s: %s" % (self.name, self.color))

    def __str__(self):
        return "P"

    @property
    def get_color(self):
        return self.color

    @property
    def get_store(self):
        return self.store

    def next(self):
        board = self.board.board
        if self in self.board.flat:
            x, y = self.x, self.y

            nextx, nexty = edit_pos(self.pos, CONVERT_DIRECTIONAL[self.d])

            coords_bool = nextx in range(self.board.width) and nexty in range(self.board.height)

            if coords_bool and type(board[nextx][nexty]) is EmptyCell:
                track = Track(x, y, self.board, self, (self.d, REVERSE_DIRECTIONAL[self.old_d]))
                board[self.x][self.y] = track
                self.tracks.append(track)
                self.edit_dir(self.d)
                self.store.add_points(settings['points_price'][game_difficulty])

                self.x, self.y = nextx, nexty
                board[self.x][self.y] = self
                self.next_count += 1
            elif coords_bool and type(board[nextx][nexty]) is Player:
                board[nextx][nexty].delete()
                self.delete()
            else:
                self.delete()
            self.step = True

    def render(self, surface):
        m = models['players'][self.d[0]]
        m.render(surface, self.board.rect(self.pos), self.color)

    def edit_dir(self, dir):
        if self.d != REVERSE_DIRECTIONAL[dir]:
            self.old_d = self.d
            self.d = dir

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.step:
            if str(event.key) in self.control:
                self.edit_dir(self.control[str(event.key)])
                self.step = False

    def delete(self, full=False):

        self.store.save_store()
        print_debug(self.store)
        self.board.board[self.x][self.y] = EmptyCell(self.x, self.y, self.board)
        if not full:
            self.board.board[self.startx][self.starty] = Player(*self.start, self.board, self.name)


class Track(EmptyCell):
    def __init__(self, x, y, board, player, dirs=(CENTER, UP)):
        super().__init__(x, y, board)
        self.player = player
        self.start_dir, self.end_dir = dirs

    def __str__(self):
        return "T"

    def render(self, surface):
        m = models['tracks'][''.join(sorted([self.start_dir[0], self.end_dir[0]]))]
        m.render(surface, self.board.rect(self.pos), self.player.get_color)

    def update(self, *args):
        if self.player not in self.board.flat:
            self.board.board[self.x][self.y] = EmptyCell(self.x, self.y, self.board)


class Board:
    def __init__(self, width=100, height=100, players_name=settings['players_name'], cell_size=30,
                 top=None, left=None, bottom=None, right=None,
                 border_color="white", grid_color="white"):
        all_boards.append(self)
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.top = 10
        self.bottom = 10
        self.left = 10
        self.right = 10
        self.players_name = players_name
        start_pos = [tuple(settings["players"][i]["start_pos"]) for i in players_name]
        self.grid = True
        self.border = True

        self.border_color = to_color(border_color)
        self.grid_color = to_color(grid_color)

        self.set_view(top, left, bottom, right, cell_size, border_color, grid_color)

        player_index = 0
        self.board = [[]]
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in start_pos:
                    self.board[-1].append(Player(x, y, self, settings['players_name'][player_index]))
                    player_index += 1
                else:
                    self.board[-1].append(EmptyCell(x, y, self))
            self.board.append([])

    def set_board(self, board):
        self.board = board

    def set_view(self, top=None, left=None, bottom=None, right=None, cell_size=None,
                 border_color=None, grid_color=None):
        self.top = top if top is not None else self.top
        self.left = left if left is not None else self.left
        self.bottom = bottom if bottom is not None else self.bottom
        self.right = right if right is not None else self.right
        self.cell_size = cell_size if cell_size is not None else self.cell_size
        self.border_color = to_color(border_color) if border_color is not None else self.border_color
        self.grid_color = to_color(grid_color) if grid_color is not None else self.grid_color

    def show_grid(self, lever=None):
        self.grid = (not self.grid) if lever is None else bool(lever)

    def show_border(self, lever=None):
        self.border = (not self.border) if lever is None else bool(lever)

    @property
    def get_size(self):
        return self.width * self.cell_size + self.left + self.right, \
               self.height * self.cell_size + self.top + self.bottom

    @property
    def flat(self):
        return list(j for i in self.board for j in i)

    @property
    def get_players(self):
        return list(filter(lambda x: type(x) is Player, self.flat))

    @staticmethod
    def rotate(array, rotate=1):
        res = array
        for i in range(rotate):
            res = list(zip(*res[::-1]))
        return res

    @property
    def global_rect(self):
        return pygame.Rect((self.left, self.top), (self.width*self.cell_size, self.height*self.cell_size))

    def __iter__(self):
        return self.flat

    def render(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                render = getattr(self.board[x][y], "render", None)
                if callable(render):
                    self.board[x][y].render(surface)
                if self.grid:
                    pygame.draw.rect(surface, self.grid_color, self.rect(x, y), 1)
                if self.border:
                    pygame.draw.rect(surface, self.border_color, self.global_rect, 1)

    def rect(self, x, y=None):
        if y is None:
            x, y = x
        return pygame.Rect(self.left + (x * self.cell_size), self.top + (y * self.cell_size),
                           self.cell_size, self.cell_size)

    def get_event(self, event):
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

    def delete(self):
        for i in self.flat:
            i.delete(True)


class Data:
    def __init__(self, rect, board, color):
        self.rect: pygame.Rect = rect
        self.board: Board = board
        self.color = to_color(color)
        self.font_size = 32
        self.font = pygame.font.Font(None, self.font_size)

    def text(self, text, color, surface, pos=0):
        rendered_text = self.font.render(text, 1, color)
        rendered_rect = rendered_text.get_rect(y=self.rect.y + 20 + pos * self.font_size // 1.5, centerx=self.rect.centerx)
        surface.blit(rendered_text, rendered_rect)

    def render_bg(self, surface):
        surface.fill(self.color, self.rect)


class RightData(Data):
    def render(self, surface):
        self.render_bg(surface)
        store = [{"name": i.name, "store": i.get_store, "color": i.color} for i in self.board.get_players]
        store.sort(key=lambda x: (int(x['store']), x['store'].get_hs), reverse=True)
        hs = [{"name": i['name'], "store": i['store'].get_hs, "color": i['color']} for i in store]

        hs = list(sorted(hs, key=lambda x: (int(x['store']), x['name']), reverse=True))
        res = ['Total Store:'] + store + ['', '', '', 'High Store:'] + hs
        for i in range(len(res)):
            self.text(*(("%s: %d" % (res[i]['name'], int(res[i]['store'])), res[i]['color'])
                        if type(res[i]) is dict else (res[i], to_color("white"))), surface, i)

# INTERFACE


def start_screen(surface, clock):
    intro_text = ["НАЗВАНИЕ ИГРЫ", "", "Правила игры:", "Если в правилах несколько строк,",
                  "приходится выводить построчно"]
    surface.fill(pygame.Color("darkgreen"))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color("white"))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        surface.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
            music_volume_event(event)

        pygame.display.flip()
        clock.tick(settings['FPS'])


def paused_screen(surface: pygame.Surface, clock: pygame.time.Clock()):
    screen = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    screen.fill(pygame.Color(0, 0, 0, 150))
    rect: pygame.Rect = surface.get_rect()
    logo: pygame.Surface = LOGO_IMAGE
    logo_center = rect.centerx, rect.centery // 3
    logo_rect: pygame.Rect = logo.get_rect()
    logo_rect.center = logo_center
    screen.blit(logo, logo_rect)
    surface.blit(screen, rect)
    ok_rect = pygame.Rect(0, 0, 300, 40)
    ex_rect = pygame.Rect(0, 0, 300, 40)
    ok_rect.centerx, ok_rect.centery = rect.centerx, rect.centery + rect.centery // 4
    ex_rect.centerx, ex_rect.centery = rect.centerx, rect.centery + rect.centery // 4 * 2
    ok = Button(ok_rect, "Продолжить", bg_color=pygame.Color("green"), active_color=pygame.Color("lightgreen"))
    ex = Button(ex_rect, "Выйти", bg_color=pygame.Color("red"), active_color=pygame.Color("#ff5c77"))
    label_rect = logo_rect.copy()
    label_rect.center = rect.center
    gui = GUI(Label(label_rect, "ПАУЗА", "white"),
              ok, ex)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and pygame.key == pygame.K_SPACE:
                return True
            music_volume_event(event, -0.01)
            gui.get_event(event)

        gui.render(surface)
        gui.update()
        if ok:
            return True
        elif ex:
            return False
        pygame.display.flip()


if __name__ == '__main__':
    b = create_board()
    print_debug(b.get_size)
