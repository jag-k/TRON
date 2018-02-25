import numpy as np

import os

import pygame

from select_method import select

SYMBOL_CODE = {
    "■": True,
    "□": False
}

REVERSED_SYMBOL_CODE = {
    True: "■",
    False: "□"
}


def model_name_format(s=str()):
    return os.path.join('data', 'models', s.lower().strip().rstrip('.model') + '.model')


def save():
    with open(model_name, 'w') as file:
        file.write(raw)
    print('Model \x1b[4;1;32m%s\x1b[0m was been %s!' % (model_name, ['created', 're-saved'][edited]))


class Board:
    def __init__(self, width=100, height=100, cell_size=30):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.top = 10
        self.left = 10
        self.board = [[0 for y in range(height)] for x in range(width)]

    @property
    def get_size(self):
        return self.width * self.cell_size + self.left * 2, self.height * self.cell_size + self.top * 2

    def rect(self, x, y):
        return pygame.Rect(self.left + (x * self.cell_size), self.top + (y * self.cell_size),
                           self.cell_size, self.cell_size)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, (0, 255, 0) if x == self.width//2 or y == self.height//2 else (255, 255, 255),
                                 self.rect(x, y), int(not self.board[x][y]))

    def on_click(self, cell):
        x, y = cell
        self.board[x][y] = not self.board[x][y]

    def get_cell(self, mouse_pos):
        x_pos, y_pos = mouse_pos[0] - self.left, mouse_pos[1] - self.top
        if x_pos >= 0 and y_pos >= 0 and x_pos // self.cell_size < self.width and y_pos // self.cell_size < self.height:
            return x_pos // self.cell_size, y_pos // self.cell_size

    def get_cell_status(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            return self.board[cell[0]][cell[1]]

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


pygame.init()
edited = False

if select('Select', 'edit', 'create')[0] == 'edit':
    model_name = model_name_format(select("Select Model",
                                          *list(filter(lambda x: x.endswith('.model'), os.listdir('data/models/'))))[0])
    size = len(open(model_name).readline())-1
    model = [[SYMBOL_CODE[j] for j in i] for i in open(model_name).read().split('\n')]
    edited = True
else:
    model_name = None
    size = int(input("Enter the size model (NxN): "))

board = Board(size, size, 10)
if model_name is not None:
    board.board = list(np.transpose(np.array(model)))
size = width, height = board.get_size
screen = pygame.display.set_mode(size)
running = True
drawing = False


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.get_click(event.pos)
                if not drawing:
                    drawing = bool(board.get_cell_status(event.pos))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drawing = False

        if event.type == pygame.MOUSEMOTION and drawing:
            if not board.get_cell_status(event.pos):
                board.get_click(event.pos)

    screen.fill((0, 0, 0))
    board.render()
    pygame.display.flip()

raw = '\n'.join(''.join(REVERSED_SYMBOL_CODE[j] for j in i)
                for i in np.transpose(np.array(board.board)))
pygame.quit()


try:
    if model_name is None:
        model_name = model_name_format(input('Enter model name (without \x1b[4;1m.model\x1b[0m expand): '))
        save()
    elif select('Save model?'):
        save()
except KeyboardInterrupt:
    print('\n\x1b[31mMODEL DOESN\'T SAVE\x1b[0m')
    SystemExit()
