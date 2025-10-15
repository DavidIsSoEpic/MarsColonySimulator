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
from power_generator_inventory import PowerGeneratorInventory
from power_generator import PowerGenerator

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

    # Filter resources outside base
    all_resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)
    resources = []
    base_rect = pygame.Rect(base.x * TILE_SIZE - 5, base.y * TILE_SIZE - 5,
                            base.radius * TILE_SIZE * 2 + 10, base.radius * TILE_SIZE * 2 + 10)
    for res in all_resources:
        filtered_positions = [(x, y) for x, y in res.positions
                              if not base_rect.collidepoint(x * TILE_SIZE, y * TILE_SIZE)]
        if filtered_positions:
            res.positions = filtered_positions
            resources.append(res)

    building_manager.set_resources(resources)
    building_manager.set_base(base)

    # --- Units ---
    units = []
    selected_unit = None

    # --- Inventories ---
    show_rover_inventory = False
    rover_inventory = None
    show_drone_inventory = False
    drone_inventory = None
    show_base_inventory = False
    base_inventory = BaseInventory(base, None)
    show_vehicle_inventory = False
    vehicle_inventory = None
    show_power_inventory = False
    power_inventory = None

    bottom_right_message = ""
    message_timer = 0
    placing_building = None
    ignore_next_click = False
    rotate_pressed_last_frame = False

    # --- Dashboard ---
    dashboard = Dashboard(rounds_total=30)
    dashboard.food = 50
    dashboard.water = 30
    dashboard.power = 20
    dashboard.metals = 10
    dashboard.population = 5
    dashboard.soldiers = 0
    dashboard.current_event = ""
    base_inventory.dashboard = dashboard

    # --- Event manager ---
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)
    clock = pygame.time.Clock()
    running = True

    # --- Message helper ---
    def set_message(msg, duration=2.0):
        nonlocal bottom_right_message, message_timer
        bottom_right_message = msg
        message_timer = duration

    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # Rotate building if placing
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

            # --- Handle inventories ---
            if show_rover_inventory and rover_inventory:
                action = rover_inventory.handle_event(event, resources)
                if action == "close":
                    show_rover_inventory = False
                    ignore_next_click = True
                clicked_ui = True

            if show_drone_inventory and drone_inventory:
                action = drone_inventory.handle_event(event, resources)
                if action == "close":
                    show_drone_inventory = False
                    ignore_next_click = True
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
                elif action in ("buy_rover", "buy_drone"):
                    # handle purchase
                    spawn_x = (vehicle_inventory.vehicle_bay["gx"] + vehicle_inventory.vehicle_bay["size"][0] // 2) * TILE_SIZE + TILE_SIZE // 2
                    spawn_y = (vehicle_inventory.vehicle_bay["gy"] + vehicle_inventory.vehicle_bay["size"][1] // 2) * TILE_SIZE + TILE_SIZE // 2
                    if action == "buy_rover":
                        if dashboard.metals >= 5:
                            new_rover = Rover(spawn_x, spawn_y)
                            new_rover.storage = 0
                            new_rover.resources_held = {}
                            new_rover.mining_active = False
                            new_rover.awaiting_move_confirmation = False
                            new_rover.move_count = 0
                            new_rover.max_moves = 2
                            units.append(new_rover)
                            dashboard.metals -= 5
                            set_message("Rover constructed!")
                            show_vehicle_inventory = False
                        else:
                            set_message("Not enough metal for Rover")
                    elif action == "buy_drone":
                        if dashboard.metals >= 10:
                            new_drone = Drone(spawn_x, spawn_y - TILE_SIZE)
                            new_drone.storage = 0
                            new_drone.resources_held = {}
                            new_drone.mining_active = False
                            new_drone.awaiting_move_confirmation = False
                            new_drone.move_count = 0
                            new_drone.max_moves = 2
                            units.append(new_drone)
                            dashboard.metals -= 10
                            set_message("Drone constructed!")
                            show_vehicle_inventory = False
                        else:
                            set_message("Not enough metal for Drone")
                clicked_ui = True

            if show_power_inventory and power_inventory:
                action = power_inventory.handle_event(event)
                if action == "close":
                    show_power_inventory = False
                clicked_ui = True

            # --- Handle world clicks ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                if ignore_next_click:
                    ignore_next_click = False
                    continue

                # Right-click: unit/building inventory
                if event.button == 3:
                    clicked_on_unit = False
                    for u in units:
                        if u.is_clicked(click_pos):
                            if isinstance(u, Rover):
                                rover_inventory = RoverInventory(u)
                                show_rover_inventory = not show_rover_inventory
                            elif isinstance(u, Drone):
                                drone_inventory = DroneInventory(u)
                                show_drone_inventory = not show_drone_inventory
                            clicked_on_unit = True
                            break
                    if clicked_on_unit:
                        clicked_ui = True
                        continue

                    # Power generator inventory
                    for b in building_manager.buildings:
                        gx, gy, bsize, b_type = b["gx"], b["gy"], b["size"], b["type"]
                        rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, bsize[0]*TILE_SIZE, bsize[1]*TILE_SIZE)
                        if b_type == "Power Generator" and rect.collidepoint(click_pos):
                            if "object" in b:
                                power_inventory = PowerGeneratorInventory(b["object"], dashboard)
                                show_power_inventory = True
                                clicked_ui = True
                                break

                    # Vehicle Bay inventory
                    for b in building_manager.buildings:
                        gx, gy, bsize, b_type = b["gx"], b["gy"], b["size"], b["type"]
                        rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, bsize[0]*TILE_SIZE, bsize[1]*TILE_SIZE)
                        if b_type == "Vehicle Bay" and rect.collidepoint(click_pos):
                            vehicle_inventory = VehicleBayInventory(b, dashboard)
                            show_vehicle_inventory = True
                            clicked_ui = True
                            break

                    # Base inventory
                    base_rect_px = pygame.Rect(base.x*TILE_SIZE - base.radius*TILE_SIZE,
                                               base.y*TILE_SIZE - base.radius*TILE_SIZE,
                                               base.radius*2*TILE_SIZE, base.radius*2*TILE_SIZE)
                    if base_rect_px.collidepoint(click_pos) and not clicked_ui:
                        show_base_inventory = not show_base_inventory
                        clicked_ui = True

                # Left-click: unit movement or building placement
                elif event.button == 1:
                    # Dashboard actions
                    action = dashboard.handle_click(click_pos)
                    if action == "next_round":
                        dashboard.food = max(dashboard.food - dashboard.population*2, 0)
                        dashboard.water = max(dashboard.water - dashboard.population*1, 0)
                        for u in units:
                            if getattr(u, "mining_active", False):
                                u.storage += 1
                                set_message(f"{u.__class__.__name__} mined 1 unit. Total: {u.storage}", 2.0)
                            u.move_count = 0
                        continue
                    elif action == "stop_control":
                        selected_unit = None
                        set_message("Stopped controlling unit", 1.5)
                        continue

                    # Placement or movement
                    if placing_building:
                        b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                        b_size = b_info.get("size", (4, 4))
                        cost = b_info["cost"].get("metals", 0)
                        new_obj = PowerGenerator if placing_building == "Power Generator" else None
                        if dashboard.metals >= cost:
                            if building_manager.add_building(click_pos[0]//TILE_SIZE, click_pos[1]//TILE_SIZE,
                                                            size=b_size, color=(200,200,200),
                                                            b_type=placing_building,
                                                            obj=new_obj(gx=click_pos[0]//TILE_SIZE,
                                                                        gy=click_pos[1]//TILE_SIZE) if new_obj else None):
                                dashboard.metals -= cost
                                set_message(f"Placed {placing_building} at {click_pos[0]//TILE_SIZE},{click_pos[1]//TILE_SIZE}")
                                placing_building = None
                            else:
                                set_message("Invalid building spot")
                        else:
                            set_message("Not enough metals")
                    else:
                        # Unit selection/movement
                        clicked_on_unit = False
                        for u in units:
                            if u.is_clicked(click_pos):
                                selected_unit = u
                                clicked_on_unit = True
                                break
                        if not clicked_on_unit and selected_unit:
                            if getattr(selected_unit, "move_count", 0) >= getattr(selected_unit, "max_moves", 9999):
                                set_message(f"{selected_unit.__class__.__name__} has no moves left this round")
                            else:
                                if getattr(selected_unit, "mining_active", False):
                                    if not getattr(selected_unit, "awaiting_move_confirmation", False):
                                        set_message("This unit is mining. Click again to move it.")
                                        selected_unit.awaiting_move_confirmation = True
                                    else:
                                        selected_unit.awaiting_move_confirmation = False
                                        selected_unit.mining_active = False
                                        selected_unit.set_target(click_pos)
                                        selected_unit.move_count += 1
                                else:
                                    selected_unit.set_target(click_pos)
                                    selected_unit.move_count += 1

        # ---------------- Updates ---------------- #
        event_manager.update(dt)
        for u in units:
            if isinstance(u, Rover):
                u.move(noise_map, TILE_SIZE, COLS, ROWS, dt)
            else:
                u.move(noise_map, TILE_SIZE, COLS, ROWS)

        if rover_inventory:
            rover_inventory.update(resources)
        if drone_inventory:
            drone_inventory.update(resources)
        if base_inventory:
            base_inventory.update()
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.update()
        if show_power_inventory and power_inventory:
            power_inventory.update(dt)

        # Update total generator power for dashboard
        total_power_percent = 0
        for b in building_manager.buildings:
            if b["type"] == "Power Generator" and "object" in b:
                total_power_percent += b["object"].power
        dashboard.power = int(total_power_percent)

        # ---------------- Drawing ---------------- #
        screen.fill((0,0,0))
        draw_terrain(screen, noise_map, TILE_SIZE)
        for res in resources:
            for x,y in res.positions:
                pygame.draw.rect(screen, res.color, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        building_manager.draw(screen, TILE_SIZE)
        base.draw(screen, TILE_SIZE)
        for u in units:
            u.draw(screen)

        # Building placement preview
        if placing_building:
            gx, gy = mouse_pos[0]//TILE_SIZE, mouse_pos[1]//TILE_SIZE
            b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
            b_size = b_info.get("size",(4,4))
            valid = building_manager.can_place(gx, gy, b_size)
            color = (0,200,0) if valid else (200,0,0)
            pygame.draw.rect(screen, color, pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, b_size[0]*TILE_SIZE, b_size[1]*TILE_SIZE), 2)

        # Draw inventories
        if show_rover_inventory and rover_inventory:
            rover_inventory.draw(screen, resources)
        if show_drone_inventory and drone_inventory:
            drone_inventory.draw(screen, resources)
        if show_base_inventory:
            base_inventory.draw(screen)
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.draw(screen)
        if show_power_inventory and power_inventory:
            power_inventory.draw(screen)

        # Dashboard and stop control button
        dashboard.draw(screen)
        try:
            padding = 10
            sw = screen.get_width()
            btn_w, btn_h = dashboard.button_width, dashboard.button_height
            stop_rect = pygame.Rect(sw - btn_w - padding, padding + btn_h + 8, btn_w, btn_h)
            dashboard.stop_control_button = stop_rect
            pygame.draw.rect(screen, (200,50,50), stop_rect, border_radius=6)
            pygame.draw.rect(screen, (255,255,255), stop_rect, 2, border_radius=6)
            txt = dashboard.button_font.render("Stop Controlling", True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=stop_rect.center))
        except Exception:
            pass

        event_manager.draw(screen)

        # Bottom-right message
        if bottom_right_message and message_timer>0:
            msg_font = pygame.font.SysFont("Arial", 20, bold=True)
            msg_text = msg_font.render(bottom_right_message, True, (255,255,255))
            screen.blit(msg_text, (WIDTH-msg_text.get_width()-20, HEIGHT-msg_text.get_height()-20))
            message_timer -= dt
        elif message_timer<=0:
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


