import pygame

class Dashboard:
    def __init__(self, rounds_total, font_size=24, color=(255, 255, 255)):
        """
        rounds_total: total number of rounds/turns
        """
        self.current_round = 1
        self.rounds_total = rounds_total
        self.color = color
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)

        # metrics
        self.population = 100
        self.food = 50
        self.power = 50
        self.water = 50
        self.soldiers = 10
        self.metals = 20
        self.current_event = "None"

    def next_round(self):
        """Increment the current round."""
        if self.current_round < self.rounds_total:
            self.current_round += 1

    def update_metrics(self, population=None, food=None, power=None,
                       water=None, soldiers=None, metals=None,
                       current_event=None):
        """Update metrics values."""
        if population is not None: self.population = population
        if food is not None: self.food = food
        if power is not None: self.power = power
        if water is not None: self.water = water
        if soldiers is not None: self.soldiers = soldiers
        if metals is not None: self.metals = metals
        if current_event is not None: self.current_event = current_event

    def draw_text_with_outline(self, screen, text, x, y, outline_color=(0,0,0)):
        """Draw text with black outline."""
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx != 0 or dy != 0:
                    outline = self.font.render(text, True, outline_color)
                    screen.blit(outline, (x + dx, y + dy))
        render = self.font.render(text, True, self.color)
        screen.blit(render, (x, y))

    def draw(self, screen):
        """Draw the full dashboard panel."""
        x = 10
        y = 10
        line_height = self.font.get_height() + 4

        self.draw_text_with_outline(screen, f"Round: {self.current_round}/{self.rounds_total}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, "-"*20, x, y)
        y += line_height

        self.draw_text_with_outline(screen, f"Population: {self.population}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, f"Food: {self.food}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, f"Power: {self.power}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, f"Water: {self.water}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, f"Soldiers: {self.soldiers}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, f"Metals: {self.metals}", x, y)
        y += line_height
        self.draw_text_with_outline(screen, "-"*20, x, y)
        y += line_height

        self.draw_text_with_outline(screen, f"Current Event: {self.current_event}", x, y)
