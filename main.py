from lib import *

import pygame
pygame.init()


def load_image(name, colorkey=None):
    fullname = join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


board = create_board()
size = width, height = board.get_size
running = True
paused = False
fps = 60
clock = pygame.time.Clock()
bg = pygame.Color(settings['textures']['game']['color_bg'])
pygame.display.set_caption(settings['textures']['window']['title'])
pygame.display.set_icon(pygame.image.load(join('data', 'images', settings['textures']['window']['icon'])))

init_music()

screen = pygame.display.set_mode(size)
start_screen(clock, size)
right_data = RightData(pygame.Rect((screen.get_width()-200, 0), (200, screen.get_height())), board, "gray35")
pygame.time.set_timer(25, settings['difficult'][game_difficult]['game_speed'])

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == 25 and not paused:
            board.next_step()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                get_screenshot(screen)
            if event.key == pygame.K_ESCAPE:
                if not paused_screen(screen, clock):
                    terminate()
            if event.key == pygame.K_r:
                board = create_board()
            if event.key == pygame.K_SPACE and settings['debug']:
                paused = not paused
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h and settings['debug']:
                board.show_grid()
        board.get_event(event)
        music_volume_event(event)

    if not paused:
        screen.fill(bg)
        board.render(screen)
        board.update()
        right_data.render(screen)
    pygame.display.flip()

terminate()
