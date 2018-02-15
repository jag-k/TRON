import pygame

import os

pygame.init()

SYMBOL_CODE = {"□": None,
               "■": 'C'}


def to_color(color):
    if color is None:
        return None
    if type(color) is pygame.Color:
        return color
    if type(color) is tuple:
        return pygame.Color(*color)
    return pygame.Color(color)


class Model:
    def __init__(self, model_name):
        self.model = self.update(model_name)

    def __repr__(self):
        return '<Model at "%s.model">' % self.model['name']

    def render(self, surface, rect, color):
        image = pygame.transform.scale(self.image(color, self.model), rect.size)
        surface.blit(image, rect)

    @staticmethod
    def image(color, model):
        color = to_color(color)
        if color is None:
            return None
        image = pygame.Surface(model['size'], pygame.SRCALPHA)
        for y in range(model['y']):
            for x in range(model['x']):
                if model['model'][x][y] is not None:
                    pygame.draw.line(image, to_color(color), (y, x), (y, x))
        return image

    @staticmethod
    def update(model_name):
        model = {"name": os.path.split(model_name)[-1].lower().rstrip('.model')}
        model["full_name"] = os.path.join('data', 'models', model["name"]+'.model')
        model['raw'] = [[y for y in x] for x in map(lambda x: x.strip(), open(model['full_name']).readlines())]

        model['model'] = [[SYMBOL_CODE[model['raw'][x][y]]
                           for y in range(len(model['raw'][x]))]
                          for x in range(len(model['raw']))]

        model['size'] = model['x'], model['y'] = len(model['raw']), len(model['raw'][0])
        return model


if __name__ == '__main__':
    size = width, height = 600, 400
    screen = pygame.display.set_mode(size)
    color = (255, 5, 20)
    p = Model('r_player')
    t = Model('dr_track')
    c = Model('cu_track')
    r = Model('du_track')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 255, 0))
        t.render(screen, pygame.Rect(25, 25, 100, 100), color)
        p.render(screen, pygame.Rect(125, 25, 100, 100), color)
        r.render(screen, pygame.Rect(25, 125, 100, 100), color)
        c.render(screen, pygame.Rect(25, 225, 100, 100), color)

        pygame.display.flip()

    pygame.quit()
