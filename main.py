import pygame
from rover import Rover
from terrain import generate_noise_map, draw_terrain
import numpy as np

pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")

# ---------------- Main Loop ---------------- #
def main():
    noise_map = generate_noise_map(ROWS, COLS)
    rover = Rover(WIDTH // 2, HEIGHT // 2)  # initialize rover
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rover.set_target(event.pos)

        draw_terrain(screen, noise_map, TILE_SIZE)
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()





# git init
# git add .
# git add main.py
# git commit -m (COMMENT)
# git push -u origin main