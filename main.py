from lib import *


pygame.init()


def create_board():
    b = Board(40, 40, 15, (5, 5), (30, 30))
    b.edit_padding(left=0, bottom=0, top=35, right=0)
    return b


board = create_board()
size = width, height = board.get_size
screen = pygame.display.set_mode(size)
running = True
paused = False

clock = pygame.time.Clock()
bg = pygame.Color("gray45")

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

        board.get_event(event)

    screen.fill(bg)
    board.render(screen)
    board.update()
    pygame.display.flip()

terminate()
