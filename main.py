import pygame
from rover import Rover
from drone import Drone
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu
from resources import ResourceDeposit
from rover_inventory import RoverInventory

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
    rover.storage = 0
    rover.mining_active = False
    rover.awaiting_move_confirmation = False
    drone = Drone(base.x * TILE_SIZE + 50, base.y * TILE_SIZE + 50)

    selected_unit = None
    show_rover_inventory = False
    rover_inventory = RoverInventory(rover)

    bottom_right_message = ""
    message_timer = 0

    # Initialize dashboard
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

    # Event Manager
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    # Spawn resources
    resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        mouse_held = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            clicked_ui = False
            if show_rover_inventory:
                action = rover_inventory.handle_event(event, resources)
                if action == "close":
                    show_rover_inventory = False
                # Prevent rover from moving if click was on Mine or X
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    mine_rect = pygame.Rect(rover_inventory.x + 50,
                                            rover_inventory.y + rover_inventory.height - 70,
                                            rover_inventory.width - 100, 50)
                    x_rect = pygame.Rect(rover_inventory.x + rover_inventory.width - 35,
                                         rover_inventory.y + 5, 30, 30)
                    if mine_rect.collidepoint(click_pos) or x_rect.collidepoint(click_pos):
                        clicked_ui = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                clicked_on_unit = False

                # Right-click opens rover inventory
                if event.button == 3 and rover.is_clicked(click_pos):
                    show_rover_inventory = not show_rover_inventory

                # Left-click selects unit
                if event.button == 1:
                    if rover.is_clicked(click_pos):
                        selected_unit = rover
                        clicked_on_unit = True
                    elif drone.is_clicked(click_pos):
                        selected_unit = drone
                        clicked_on_unit = True

                    # Only move if not clicked on unit or UI
                    if not clicked_on_unit and not clicked_ui and selected_unit:
                        # Handle rover mining prevention
                        if isinstance(selected_unit, Rover) and selected_unit.mining_active:
                            if not selected_unit.awaiting_move_confirmation:
                                bottom_right_message = "This Rover is mining. Click again to move it."
                                message_timer = 3
                                selected_unit.awaiting_move_confirmation = True
                            else:
                                selected_unit.awaiting_move_confirmation = False
                                selected_unit.mining_active = False
                                rover_inventory.mining = False
                                selected_unit.set_target(click_pos)
                        else:
                            selected_unit.set_target(click_pos)

                # Update dashboard per turn (food/water)
                dashboard.next_round()
                new_food = max(dashboard.food - dashboard.population * 2, 0)
                new_water = max(dashboard.water - dashboard.population * 1, 0)
                dashboard.update_metrics(food=new_food, water=new_water)

        # Update events
        event_manager.update(dt)

        # Update mining and inventory
        rover_inventory.update(resources)

        # ---------------- Draw Everything ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        base.draw(screen, TILE_SIZE)

        # Draw resources behind units
        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, res.color, rect)

        # Move and draw units
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)

        drone.move(noise_map, TILE_SIZE, COLS, ROWS)
        drone.draw(screen)

        # Draw RoverInventory on top if active
        if show_rover_inventory:
            rover_inventory.draw(screen, resources)

        # Draw dashboard and events on top
        dashboard.draw(screen)
        event_manager.draw(screen)

        # Draw bottom-right messages
        if bottom_right_message and message_timer > 0:
            msg_font = pygame.font.SysFont("Arial", 20, bold=True)
            msg_text = msg_font.render(bottom_right_message, True, (255, 255, 255))
            screen.blit(msg_text, (WIDTH - msg_text.get_width() - 20, HEIGHT - msg_text.get_height() - 20))
            message_timer -= dt

        pygame.display.flip()


def main():
    # Main Menu
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

        if in_settings:
            menu.draw_settings_menu(screen)
        else:
            menu.draw_main_menu(screen)

        pygame.display.flip()

    # Start Game
    game_loop()


if __name__ == "__main__":
    main()


# git init
# git add .
# git commit -m (COMMENT)
# git push -u origin main
