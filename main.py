import pygame
from building_manager import BuildingManager
from rover import Rover
from drone import Drone
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu
from resources import ResourceDeposit
from rover_inventory import RoverInventory
from base_inventory import BaseInventory  # <-- Import your BaseInventory

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

    # Link building manager with noise map
    building_manager = BuildingManager(noise_map)

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
    show_base_inventory = False
    base_inventory = BaseInventory(base, None)  # Dashboard will be linked after init

    bottom_right_message = ""
    message_timer = 0

    # Initialize dashboard
    dashboard = Dashboard(rounds_total=30)
    dashboard.update_metrics(
        population=5,
        food=50,
        power=20,
        water=30,
        metals=10,  # start with more to support building placement
        soldiers=0,
        current_event=""
    )
    base_inventory.dashboard = dashboard  # Link dashboard now

    # Event Manager
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    # Spawn resources but exclude area around the base
    all_resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)
    resources = []
    base_rect = pygame.Rect(
        base.x * TILE_SIZE - 5, base.y * TILE_SIZE - 5,
        base.radius * TILE_SIZE * 2 + 10, base.radius * TILE_SIZE * 2 + 10
    )

    for res in all_resources:
        filtered_positions = []
        for x, y in res.positions:
            res_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if not base_rect.colliderect(res_rect):
                filtered_positions.append((x, y))
        if filtered_positions:
            res.positions = filtered_positions
            resources.append(res)

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

            # ---------------- Rover Inventory ---------------- #
            if show_rover_inventory:
                action = rover_inventory.handle_event(event, resources)
                if action == "close":
                    show_rover_inventory = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    mine_rect = pygame.Rect(rover_inventory.x + 50,
                                            rover_inventory.y + rover_inventory.height - 70,
                                            rover_inventory.width - 100, 50)
                    x_rect = pygame.Rect(rover_inventory.x + rover_inventory.width - 35,
                                         rover_inventory.y + 5, 30, 30)
                    if mine_rect.collidepoint(click_pos) or x_rect.collidepoint(click_pos):
                        clicked_ui = True

            # ---------------- Base Inventory ---------------- #
            if show_base_inventory:
                action = base_inventory.handle_event(event)
                if action == "close":
                    show_base_inventory = False
                clicked_ui = True  # Prevent moving units when inventory is open

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                clicked_on_unit = False

                # Right-click → either open rover/base inventory or place building
                if event.button == 3:
                    if rover.is_clicked(click_pos):
                        show_rover_inventory = not show_rover_inventory
                    elif base.is_clicked(click_pos):
                        show_base_inventory = not show_base_inventory
                    else:
                        # Place building
                        mx, my = click_pos
                        size = 2  # building size
                        gx = (mx // TILE_SIZE) // size * size
                        gy = (my // TILE_SIZE) // size * size
                        new_metals = max(dashboard.metals - dashboard.population * 0.1, 0)
                        dashboard.update_metrics(metals=new_metals)

                        if building_manager.add_building(gx, gy, size=size, color=(0, 200, 0)):
                            print(f"Placed building at {gx},{gy}")
                        else:
                            print("Invalid spot")

                # Left-click → select/move units
                elif event.button == 1:
                    if rover.is_clicked(click_pos):
                        selected_unit = rover
                        clicked_on_unit = True
                    elif drone.is_clicked(click_pos):
                        selected_unit = drone
                        clicked_on_unit = True

                    # Only move if not clicked on unit or UI
                    if not clicked_on_unit and not clicked_ui and selected_unit:
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

        # Update base inventory
        base_inventory.update()

        # ---------------- Draw Everything ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        base.draw(screen, TILE_SIZE)

        # Draw resources
        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, res.color, rect)

        # Move/draw units
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        rover.draw(screen)

        drone.move(noise_map, TILE_SIZE, COLS, ROWS)
        drone.draw(screen)

        # Draw buildings
        building_manager.draw(screen, TILE_SIZE)

        # Draw inventories on top if active
        if show_rover_inventory:
            rover_inventory.draw(screen, resources)
        if show_base_inventory:
            base_inventory.draw(screen)

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

#git init
#git add .
#git commit "COMMENT"
#git push -u origin main