from lib import *


pygame.init()
board = Board(20, 20, 25, (5, 5))
size = width, height = board.get_size
pygame.display.set_mode(size)
screen = pygame.display.get_surface()
running = True
bg = pygame.Color("blue")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                board.next_step()
            board.get_event(event)

    screen.fill(bg)
    board.render(screen, bg)
    board.update()
    pygame.display.flip()

pygame.quit()
