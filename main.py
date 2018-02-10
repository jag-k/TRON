from lib import *


pygame.init()
board = Board(20, 20, 25, (5, 5))
size = width, height = board.get_size
screen = pygame.display.set_mode(size)
running = True

clock = pygame.time.Clock()
bg = pygame.Color("darkgray")

pygame.time.set_timer(25, 180)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == 25:
            board.next_step()
        board.get_event(event)

    screen.fill(bg)
    board.render(screen, bg)
    board.update()
    pygame.display.flip()

pygame.quit()
