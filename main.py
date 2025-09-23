import pygame
from rover import Rover
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu

pygame.font.init()
pygame.init()


WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")


# game loop
def game_loop():

    noise_map = generate_noise_map(ROWS, COLS)


    base = Base.spawn(noise_map, COLS, ROWS, TILE_SIZE)


    rover = Rover(base.x * TILE_SIZE, base.y * TILE_SIZE)

    # dash
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

    # Event manager
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rover.set_target(event.pos)
                dashboard.next_round()


                new_food = max(dashboard.food - dashboard.population * 2, 0)
                new_water = max(dashboard.water - dashboard.population * 1, 0)
                dashboard.update_metrics(food=new_food, water=new_water)


        event_manager.update(dt)


        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        base.draw(screen, TILE_SIZE)
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)
        dashboard.draw(screen)
        event_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()


# main menu
def main():
    menu = Menu(WIDTH, HEIGHT)
    in_menu = True
    in_settings = False

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_held = pygame.mouse.get_pressed()[0] 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if in_settings:
                result = menu.handle_events(event, in_settings=True, mouse_pos=mouse_pos, mouse_held=mouse_held)
                if result == "back":
                    in_settings = False
            else:
                result = menu.handle_events(event)
                if result == "start":
                    in_menu = False
                elif result == "settings":
                    in_settings = True
                elif result == "quit":
                    running = False


        if in_settings:
            menu.draw_settings_menu(screen)
        elif in_menu:
            menu.draw_main_menu(screen)
        else:
            game_loop()
            running = False  

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()





# git init
# git add .
# git commit -m (COMMENT)
# git push -u origin main