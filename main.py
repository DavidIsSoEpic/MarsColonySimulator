import pygame
from rover import Rover
from drone import Drone
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu
from resources import ResourceDeposit

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

    # Initialize rover and drone
    rover = Rover(base.x * TILE_SIZE, base.y * TILE_SIZE)
    drone = Drone(base.x * TILE_SIZE + 50, base.y * TILE_SIZE + 50)  # start slightly offset

    selected_unit = None  # currently selected unit

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

    # Spawn resources
    resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000  # delta time in seconds
        mouse_pos = pygame.mouse.get_pos()
        mouse_held = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                clicked_on_unit = False

                # Check if we clicked on the rover
                if rover.is_clicked(click_pos):
                    selected_unit = rover
                    clicked_on_unit = True
                # Check if we clicked on the drone
                elif drone.is_clicked(click_pos):
                    selected_unit = drone
                    clicked_on_unit = True

                # Only move the selected unit if click was not on a unit
                if not clicked_on_unit and selected_unit:
                    selected_unit.set_target(click_pos)

                # Update resources / dashboard per turn
                dashboard.next_round()
                new_food = max(dashboard.food - dashboard.population * 2, 0)
                new_water = max(dashboard.water - dashboard.population * 1, 0)
                dashboard.update_metrics(food=new_food, water=new_water)

        # ---------------- Update Events ---------------- #
        event_manager.update(dt)

        # ---------------- Draw Everything ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        base.draw(screen, TILE_SIZE)

        # Draw resources behind dashboard
        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, res.color, rect)

        # Move and draw units
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)

        drone.move(noise_map, TILE_SIZE, COLS, ROWS)
        drone.draw(screen)

        # Draw dashboard on top
        dashboard.draw(screen)

        # Draw events on top
        event_manager.draw(screen)

        pygame.display.flip()


def main():
    # ----------- Main Menu Loop ----------- #
    menu = Menu(WIDTH, HEIGHT)
    in_menu = True
    in_settings = False

    while in_menu:
        mouse_pos = pygame.mouse.get_pos()
        mouse_held = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            result = menu.handle_events(event, in_settings=in_settings, mouse_pos=mouse_pos, mouse_held=mouse_held)
            if result == "start":
                in_menu = False
            elif result == "quit":
                pygame.quit()
                return
            elif result == "settings":
                in_settings = True
            elif result == "back":
                in_settings = False

        # Draw menu
        if in_settings:
            menu.draw_settings_menu(screen)
        else:
            menu.draw_main_menu(screen)

        pygame.display.flip()

    # ----------- Start Game ----------- #
    game_loop()


if __name__ == "__main__":
    main()







# git init
# git add .
# git commit -m (COMMENT)
# git push -u origin main