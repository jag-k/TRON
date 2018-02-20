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
def main():
    pygame.display.set_mode((300, 200))
    for i in ['up', 'down', 'left', 'right']:
        print('Нажмите на кнопку для сменны направление "%s": ' % i, end='', flush=True)
        key_pressed = False
        while not key_pressed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    control[str(event.key)] = i
                    print("\x1b[32m%s\x1b[0m" % pygame.key.name(event.key), flush=True)
                    key_pressed = True

    pygame.quit()
    print(control)
    settings['players'][player]['control'] = control
    if select("Save control?"):
        json.dump(settings, open("data/settings.json", "w"), indent=2)


if __name__ == '__main__':
    main()
