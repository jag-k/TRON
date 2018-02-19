from pprint import pprint

import pygame
import json
from select_method import select
pygame.init()
settings = json.load(open('data/settings.json'))
# pprint(settings, width=120)
player = select("Выберите игрока", *settings['players_name'])[0]
# print(player)
control = {}
pygame.display.set_mode((300, 200))
for i in ['up', 'down', 'right', 'left']:
    print('Нажмите на кнопку для сменны направление "%s": ' % i, end='')
    key_pressed = False
    while not key_pressed:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                control[str(event.key)] = i
                key_pressed = True
                print(event.unicode if event.unicode.isprintable() else ("[key:%d]" % event.key))
print(control)
settings['players'][player]['control'] = control
json.dump(settings, open("settings.json", "w"), indent=2)
