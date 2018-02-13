from lib import *

import pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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
bg = pygame.Color("gray45")
pygame.display.set_icon(load_image('images/TRON_icon3.png'))
pygame.display.set_caption("-TRON_")


def start_screen():
    intro_text = ["НАЗВАНИЕ ИГРЫ", "", "Правила игры:", "Если в правилах несколько строк,",
                  "приходится выводить построчно"]
    screen.fill(pygame.Color("darkgreen"))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color("white"))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        pygame.display.flip()
        clock.tick(fps)


start_screen()
screen = pygame.display.set_mode(size)
pygame.time.set_timer(25, 180)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == 25 and not paused:
            board.next_step()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                board = create_board()
            if event.key == pygame.K_ESCAPE:
                terminate()
            if event.key == pygame.K_f:
                print("Fullscreen mode:", pygame.display.toggle_fullscreen())

        board.get_event(event)

    screen.fill(bg)
    board.render(screen)
    board.update()
    pygame.display.flip()

terminate()
