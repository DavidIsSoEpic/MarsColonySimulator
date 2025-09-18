import pygame
from rover import Rover
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu

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
def game_loop():
    # Generate terrain
    noise_map = generate_noise_map(ROWS, COLS)

    # Spawn base on safe terrain
    base = Base.spawn(noise_map, COLS, ROWS, TILE_SIZE)

    # Initialize rover at base
    rover = Rover(base.x * TILE_SIZE, base.y * TILE_SIZE)

    # Initialize dashboard with starting metrics
    dashboard = Dashboard(rounds_total=30)
    dashboard.update_metrics(
        population=5,
        food=50,
        power=20,
        water=30,
        metals=3,
        soldiers=0,
        current_event=""
    )

    # Initialize EventManager
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000  # delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rover.set_target(event.pos)
                dashboard.next_round()

                # Resource consumption per turn
                new_food = max(dashboard.food - dashboard.population * 2, 0)
                new_water = max(dashboard.water - dashboard.population * 1, 0)
                dashboard.update_metrics(food=new_food, water=new_water)

        # ---------------- Update Events ---------------- #
        event_manager.update(dt)

        # ---------------- Draw Everything ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        base.draw(screen, TILE_SIZE)
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)
        dashboard.draw(screen)
        event_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()


def main():
    # ----------- Main Menu Loop ----------- #
    menu = Menu(WIDTH, HEIGHT)
    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            result = menu.handle_events(event)
            if result == "start":
                in_menu = False
            elif result == "quit":
                pygame.quit()
                return

        menu.draw(screen)
        pygame.display.flip()

    # ----------- Start Game ----------- #
    game_loop()


if __name__ == "__main__":
    main()





# git init
# git add .
# git add main.py
# git commit -m (COMMENT)
# git push -u origin main