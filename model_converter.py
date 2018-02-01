import pygame

import os

pygame.init()


def to_color(color):
    if type(color) is pygame.Color:
        return color
    if type(color) is tuple:
        return pygame.Color(*color)
    return pygame.Color(color)


class Model:
    def __init__(self, model_name, model_size, board, color):
        model_name = os.path.split(model_name)[-1].lower().lstrip('.model')
        self.rotate = 0
        self.model_size = model_size
        self.pos = []
        self.board = board
        self.color = None if color is None else to_color(color)
        self.model = open(os.path.join(os.getcwd(), 'data', 'texture', model_name)+'.model').readlines()


    def add_position(self, x, y=None, color=None, rotate=None):
        if y is None:
            x, y = x
        if color is None:
            color = self.color
        else:
            color = to_color(color)
        if rotate is None:
            rotate = self.rotate

        self.pos.append([x, y, color, rotate])

    def update(self):
        for i in open(os.path.join(os.getcwd(), 'data', 'texture', model_name)+'.model').read().split('\n'):
            for j in

    def render(self, surface):
        for r_x, r_y, color, rotate in self.pos:
            rect: pygame.Rect = self.board.rect(r_x, r_y)
            start_x, start_y = rect.x, rect.y
            for x in range(rect.width+1):
                for y in range(rect.width+1):
                    if

