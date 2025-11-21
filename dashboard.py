# dashboard.py
import pygame
from typing import Optional, List

class Dashboard:
    def __init__(self, rounds_total: int, font_size: int = 24, color: tuple = (255, 255, 255)):
        """
        Dashboard for Mars Colony Simulator.

        Args:
            rounds_total (int): total number of rounds/turns
            font_size (int): font size for dashboard text
            color (tuple): main text color
        """
        self.current_round: int = 1
        self.rounds_total: int = rounds_total
        self.color: tuple = color
        self.font: pygame.font.Font = pygame.font.SysFont("Arial", font_size, bold=True)

        # Metrics
        self.population: int = 100
        self.food: int = 50
        self.power: int = 50
        self.water: int = 50
        self.soldiers: int = 10
        self.metals: int = 20
        self.marsium: int = 0
        self.current_event: str = "None"

        # Button appearance
        self.button_font: pygame.font.Font = pygame.font.SysFont("Arial", 20, bold=True)
        self.button_width: int = 140
        self.button_height: int = 40

        # Button positions
        screen_width: int = 1280
        padding: int = 10
        self.next_round_button: pygame.Rect = pygame.Rect(
            screen_width - self.button_width - padding, padding, self.button_width, self.button_height
        )
        self.stop_control_button: pygame.Rect = pygame.Rect(
            screen_width - self.button_width - padding,
            padding + self.button_height + 10,
            self.button_width,
            self.button_height
        )

    # ---------------- Round Logic ---------------- #
    def next_round(self, units: Optional[List] = None, building_manager: Optional[object] = None):
        """
        Advance the game by one round, updating resources, buildings, and units.

        Args:
            units (list): list of unit objects
            building_manager (object): building manager object
        """
        if self.current_round >= self.rounds_total:
            return
        self.current_round += 1

        # Decrease food & water by population
        self.food = max(self.food - self.population, 0)
        self.water = max(self.water - self.population * 0.5, 0)

        # Update Farms
        if building_manager:
            for b in building_manager.buildings:
                if b.get("type") == "Farm" and "object" in b:
                    b["object"].apply_next_round()

        # Reset units
        if units:
            for u in units:
                u.move_count = 0
                if hasattr(u, "mining_active"):
                    u.mining_active = False
                if hasattr(u, "recharging_rover"):
                    u.recharging_rover = None
                if hasattr(u, "inventory") and u.inventory:
                    u.inventory.apply_next_round_mining()

    # ---------------- Metrics ---------------- #
    def update_metrics(self, population=None, food=None, power=None,
                       water=None, soldiers=None, metals=None, current_event=None):
        """Update dashboard metrics selectively."""
        if population is not None: self.population = population
        if food is not None: self.food = food
        if power is not None: self.power = power
        if water is not None: self.water = water
        if soldiers is not None: self.soldiers = soldiers
        if metals is not None: self.metals = metals
        if current_event is not None: self.current_event = current_event

    # ---------------- Drawing ---------------- #
    def draw_text_with_outline(self, screen, text: str, x: int, y: int, outline_color=(0,0,0)):
        """Draw text with an outline for better readability."""
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx != 0 or dy != 0:
                    outline = self.font.render(text, True, outline_color)
                    screen.blit(outline, (x + dx, y + dy))
        render = self.font.render(text, True, self.color)
        screen.blit(render, (x, y))

    def draw(self, screen):
        """Draw the dashboard panel and buttons."""
        x, y = 10, 10
        line_height = self.font.get_height() + 4

        # Draw metrics
        metrics = [
            f"Round: {self.current_round}/{self.rounds_total}",
            "-"*20,
            f"Population: {self.population}",
            f"Food: {self.food}",
            f"Power: {self.power}",
            f"Water: {self.water}",
            f"Soldiers: {self.soldiers}",
            f"Metals: {self.metals}",
            f"Marsium: {self.marsium}",
            "-"*20,
            f"Current Event: {self.current_event}"
        ]
        for line in metrics:
            self.draw_text_with_outline(screen, line, x, y)
            y += line_height

        # Draw Next Round button
        if self.current_round >= self.rounds_total:
            button_color, outline_color, text_color = (120,120,120), (200,200,200), (220,220,220)
        else:
            button_color, outline_color, text_color = (0,160,60), (255,255,255), (255,255,255)

        pygame.draw.rect(screen, button_color, self.next_round_button, border_radius=6)
        pygame.draw.rect(screen, outline_color, self.next_round_button, 2, border_radius=6)
        text_surf = self.button_font.render("Next Round", True, text_color)
        text_rect = text_surf.get_rect(center=self.next_round_button.center)
        screen.blit(text_surf, text_rect)

        # Draw Stop Controlling button
        pygame.draw.rect(screen, (200,0,0), self.stop_control_button, border_radius=6)
        pygame.draw.rect(screen, (255,255,255), self.stop_control_button, 2, border_radius=6)
        stop_text = self.button_font.render("Stop Controlling", True, (255,255,255))
        stop_rect = stop_text.get_rect(center=self.stop_control_button.center)
        screen.blit(stop_text, stop_rect)

    # ---------------- Click Handling ---------------- #
    def handle_click(self, pos, units=None, building_manager=None):
        if self.next_round_button.collidepoint(pos):
            if self.current_round < self.rounds_total:
                self.next_round(units, building_manager)
                return "next_round"

        if self.stop_control_button.collidepoint(pos):
            return "stop_control"

        return None
