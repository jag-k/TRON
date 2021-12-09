import pygame

from model_converter import to_color

pygame.init()

size = width, height = 300, 200
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(to_color(input()))
    pygame.display.flip()

pygame.quit()
