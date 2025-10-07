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
from drone_inventory import DroneInventory
from base_inventory import BaseInventory
from vehicle_bay_inventory import VehicleBayInventory

pygame.font.init()
pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")


def game_loop():
    noise_map = generate_noise_map(ROWS, COLS)
    base = Base.spawn(noise_map, COLS, ROWS, TILE_SIZE)
    building_manager = BuildingManager(noise_map)

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

    building_manager.set_resources(resources)
    building_manager.set_base(base)

    # --- Create units ---
    rover = Rover(base.x * TILE_SIZE, base.y * TILE_SIZE)
    rover.storage = 0
    rover.mining_active = False
    rover.awaiting_move_confirmation = False

    drone = Drone(base.x * TILE_SIZE + 50, base.y * TILE_SIZE + 50)

    selected_unit = None

    # --- Inventories ---
    show_rover_inventory = False
    rover_inventory = RoverInventory(rover)
    show_drone_inventory = False
    drone_inventory = DroneInventory(drone)

    show_base_inventory = False
    base_inventory = BaseInventory(base, None)

    show_vehicle_inventory = False
    vehicle_inventory = None

    bottom_right_message = ""
    message_timer = 0

    placing_building = None
    ignore_next_click = False
    rotate_pressed_last_frame = False

    dashboard = Dashboard(rounds_total=30)
    dashboard.update_metrics(population=5, food=50, power=20, water=30, metals=20, soldiers=0, current_event="")
    base_inventory.dashboard = dashboard

    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # --- Rotate building if placing ---
        if placing_building:
            if keys[pygame.K_r] and not rotate_pressed_last_frame:
                b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                current_size = b_info.get("size", (4, 4))
                b_info["size"] = (current_size[1], current_size[0])
                rotate_pressed_last_frame = True
            elif not keys[pygame.K_r]:
                rotate_pressed_last_frame = False

        clicked_ui = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---------------- Inventories ---------------- #
            if show_rover_inventory:
                action = rover_inventory.handle_event(event, resources)
                if action == "close":
                    show_rover_inventory = False
                clicked_ui = True

            if show_drone_inventory:
                action = drone_inventory.handle_event(event, resources)
                if action == "close":
                    show_drone_inventory = False
                clicked_ui = True

            if show_base_inventory:
                action = base_inventory.handle_event(event)
                if action == "close":
                    show_base_inventory = False
                elif action and action.startswith("build_"):
                    placing_building = action.replace("build_", "")
                    show_base_inventory = False
                    ignore_next_click = True
                clicked_ui = True

            if show_vehicle_inventory and vehicle_inventory:
                action = vehicle_inventory.handle_event(event)
                if action == "close":
                    show_vehicle_inventory = False
                clicked_ui = True

            # ---------------- Mouse Clicks ---------------- #
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                clicked_on_unit = False

                if event.button == 3:  # Right-click
                    if rover.is_clicked(click_pos):
                        show_rover_inventory = not show_rover_inventory
                    elif drone.is_clicked(click_pos):
                        show_drone_inventory = not show_drone_inventory
                    else:
                        # Vehicle Bay
                        for b in building_manager.buildings:
                            gx, gy, bsize, b_type = b["gx"], b["gy"], b["size"], b["type"]
                            rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, bsize[0]*TILE_SIZE, bsize[1]*TILE_SIZE)
                            if b_type == "Vehicle Bay" and rect.collidepoint(click_pos):
                                vehicle_inventory = VehicleBayInventory(vehicle_bay=b, dashboard=dashboard)
                                show_vehicle_inventory = True
                        # Base
                        base_rect_px = pygame.Rect(base.x*TILE_SIZE-base.radius*TILE_SIZE, base.y*TILE_SIZE-base.radius*TILE_SIZE, base.radius*2*TILE_SIZE, base.radius*2*TILE_SIZE)
                        if base_rect_px.collidepoint(click_pos):
                            show_base_inventory = not show_base_inventory

                elif event.button == 1:  # Left-click
                    if ignore_next_click:
                        ignore_next_click = False
                        continue

                    # Check for Next Round button click
                    if dashboard.handle_click(click_pos):
                        # --- Advance round effects ---
                        new_food = max(dashboard.food - dashboard.population*2, 0)
                        new_water = max(dashboard.water - dashboard.population*1, 0)
                        dashboard.update_metrics(food=new_food, water=new_water)

                        # Rover mining logic
                        if rover.mining_active:
                            rover.storage += 1
                            bottom_right_message = f"Rover mined 1 unit. Total: {rover.storage}"
                            message_timer = 2
                        continue  # Skip other left-click actions this frame

                    gx = click_pos[0] // TILE_SIZE
                    gy = click_pos[1] // TILE_SIZE

                    if placing_building:
                        b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                        b_size = b_info.get("size", (4, 4))
                        cost = 1
                        if dashboard.metals >= cost:
                            if building_manager.add_building(gx, gy, size=b_size, color=(200, 200, 200), b_type=placing_building):
                                dashboard.update_metrics(metals=dashboard.metals - cost)
                                bottom_right_message = f"Placed {placing_building} at {gx},{gy}"
                                message_timer = 2
                                placing_building = None
                            else:
                                bottom_right_message = "Invalid building spot"
                                message_timer = 2
                        else:
                            bottom_right_message = "Not enough metals"
                            message_timer = 2
                    else:
                        if rover.is_clicked(click_pos):
                            selected_unit = rover
                            clicked_on_unit = True
                        elif drone.is_clicked(click_pos):
                            selected_unit = drone
                            clicked_on_unit = True

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

        # ---------------- Updates ---------------- #
        event_manager.update(dt)
        rover_inventory.update(resources)
        drone_inventory.update(resources)
        base_inventory.update()
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.update()

        rover.move(noise_map, TILE_SIZE, COLS, ROWS)
        drone.move(noise_map, TILE_SIZE, COLS, ROWS)

        # ---------------- Draw Everything ---------------- #
        screen.fill((0,0,0))
        draw_terrain(screen, noise_map, TILE_SIZE)

        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, res.color, rect)

        building_manager.draw(screen, TILE_SIZE)
        base.draw(screen, TILE_SIZE)

        rover.draw(screen)
        drone.draw(screen)

        if placing_building:
            gx = mouse_pos[0] // TILE_SIZE
            gy = mouse_pos[1] // TILE_SIZE
            b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
            b_size = b_info.get("size", (4,4))
            valid = building_manager.can_place(gx, gy, b_size)
            color = (0,200,0) if valid else (200,0,0)
            preview_rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, b_size[0]*TILE_SIZE, b_size[1]*TILE_SIZE)
            pygame.draw.rect(screen, color, preview_rect, 2)

        if show_rover_inventory:
            rover_inventory.draw(screen, resources)
        if show_drone_inventory:
            drone_inventory.draw(screen, resources)
        if show_base_inventory:
            base_inventory.draw(screen)
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.draw(screen)

        dashboard.draw(screen)
        event_manager.draw(screen)

        if bottom_right_message and message_timer > 0:
            msg_font = pygame.font.SysFont("Arial", 20, bold=True)
            msg_text = msg_font.render(bottom_right_message, True, (255,255,255))
            screen.blit(msg_text, (WIDTH-msg_text.get_width()-20, HEIGHT-msg_text.get_height()-20))
            message_timer -= dt
        elif message_timer <= 0:
            bottom_right_message = ""

        pygame.display.flip()


def main():
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

    game_loop()


if __name__ == "__main__":
    main()



# ---------------- Git Commands ---------------- #
# git init
# git add .
# git commit -m "Integrated DroneInventory"
# git push -u origin main
