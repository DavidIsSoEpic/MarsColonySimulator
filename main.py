import pygame
from rover import Rover
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard

pygame.font.init()
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
    dashboard = Dashboard(rounds_total=20)  # initialize dashboard
    clock = pygame.time.Clock()
    running = True

    # Set initial metrics
    dashboard.update_metrics(
        population=10,
        food=50,
        power=20,
        water=30,
        metals=10,
        soldiers=0,
        current_event=""
    )

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rover.set_target(event.pos)
                dashboard.next_round()  # increment turn only

        screen.fill((0, 0, 0))  # clear screen each frame
        draw_terrain(screen, noise_map, TILE_SIZE)
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)
        dashboard.draw(screen)  # draw the metrics panel

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