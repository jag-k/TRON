from lib import *


pygame.init()
board = Board(20, 20, 20, (5, 5))
size = width, height = board.get_size
screen = pygame.display.set_mode(size)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                board.next_step()
            board.get_event(event)

    screen.fill((0, 0, 0))
    board.render(screen)
    pygame.display.flip()

pygame.quit()
