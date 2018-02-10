import pygame

import os

pygame.init()

SYMBOL_CODE = {".": None,
               "@": 'C'}


class Model:
    def __init__(self, model_name, color=None):
        self.model = self.update(model_name, color)

    def __repr__(self):
        return '<Model at "%s.model">' % self.model['name']

    def render(self, surface, rect, color=None):
        if self.model['image'] is None:
            if color is None:
                raise ValueError
            self.model = self.update(self.model['name'], color)
        image = pygame.transform.scale(self.model['image'], rect.size)
        surface.blit(image, rect)
    
    @staticmethod
    def to_color(color):
        if color is None:
            return None
        if type(color) is pygame.Color:
            return color
        if type(color) is tuple:
            return pygame.Color(*color)
        return pygame.Color(color)

    @staticmethod
    def image(color, model):
        color = Model.to_color(color)
        if color is None:
            return None
        image = pygame.Surface(model['size'])
        for y in range(model['y']):
            for x in range(model['x']):
                if model['model'][x][y] is not None:
                    pygame.draw.line(image, Model.to_color(color), (y, x), (y, x))
        return image
    
    def update(self, model_name, color=None):
        model = {"name": os.path.split(model_name)[-1].lower().rstrip('.model')}
        model["full_name"] = os.path.join('data', 'models', model["name"]+'.model')
        model['raw'] = [[y for y in x] for x in map(lambda x: x.strip(), open(model['full_name']).readlines())]

        model['model'] = [[SYMBOL_CODE[model['raw'][x][y]]
                           for y in range(len(model['raw'][x]))]
                          for x in range(len(model['raw']))]

        model['size'] = model['x'], model['y'] = len(model['raw']), len(model['raw'][0])
        model['image'] = self.image(color, model)
        return model


if __name__ == '__main__':
    size = width, height = 600, 400
    screen = pygame.display.set_mode(size)
    color = (255, 5, 20)
    p = Model('r_player', color)
    t = Model('dr_track', color)
    c = Model('cu_track', color)
    r = Model('du_track', color)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        t.render(screen, pygame.Rect(25, 25, 100, 100))
        p.render(screen, pygame.Rect(125, 25, 100, 100))
        r.render(screen, pygame.Rect(25, 125, 100, 100))
        c.render(screen, pygame.Rect(25, 225, 100, 100))

        pygame.display.flip()

    pygame.quit()
