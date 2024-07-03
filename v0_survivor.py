import random
from enum import Enum
import pygame
import sys
from os import path

class SurvivorAction(Enum):
    LEFT=0
    DOWN=1
    RIGHT=2
    UP=3


class GridTile(Enum):
    _FLOOR=0
    SURVIVOR=1
    ZOMBIE=2
    SUPPLY=3
    DOOR=4
    WALL=5
    ROCK=6

    # Return the first letter of tile name, for printing to the console.
    def __str__(self):
        return self.name[:1]

class Survivor:

    # Initialize the grid size. Pass in an integer seed to make randomness (Targets) repeatable.
    def __init__(self, grid_rows=4, grid_cols=5, fps=1, zombies_amount=2, supplies_amount=3, walls_amount=1, rocks_amount=1):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.zombies_amount = zombies_amount
        self.supplies_amount = supplies_amount
        self.walls_amount = walls_amount
        self.rocks_amount = rocks_amount
        self.generate_random_map()
        self.reset()

        self.fps = fps
        self.last_action=''
        self._init_pygame()

    def _init_pygame(self):
        pygame.init() # initialize pygame
        pygame.display.init() # Initialize the display module

        # Game clock
        self.clock = pygame.time.Clock()

        # Default font
        self.action_font = pygame.font.SysFont("Calibre",30)
        self.action_info_height = self.action_font.get_height()

        # For rendering
        self.cell_height = 64
        self.cell_width = 64
        self.cell_size = (self.cell_width, self.cell_height)        

        # Define game window size (width, height)
        self.window_size = (self.cell_width * self.grid_cols, self.cell_height * self.grid_rows + self.action_info_height)

        # Initialize game window
        self.window_surface = pygame.display.set_mode(self.window_size) 

        # Load & resize sprites
        file_name = path.join(path.dirname(__file__), "img/survivor.png")
        img = pygame.image.load(file_name)
        self.survivor_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "img/floor.png")
        img = pygame.image.load(file_name)
        self.floor_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "img/zombie.png")
        img = pygame.image.load(file_name)
        self.zombie_img = pygame.transform.scale(img, self.cell_size) 

        file_name = path.join(path.dirname(__file__), "img/ammo.png")
        img = pygame.image.load(file_name)
        self.supply_img = pygame.transform.scale(img, self.cell_size) 

        file_name = path.join(path.dirname(__file__), "img/door.png")
        img = pygame.image.load(file_name)
        self.door_img = pygame.transform.scale(img, self.cell_size) 

        file_name = path.join(path.dirname(__file__), "img/wall.jpg")
        img = pygame.image.load(file_name)
        self.wall_img = pygame.transform.scale(img, self.cell_size) 

        file_name = path.join(path.dirname(__file__), "img/rock.png")
        img = pygame.image.load(file_name)
        self.rock_img = pygame.transform.scale(img, self.cell_size) 


    def reset(self, seed=None):
        # Initialize Robot's starting position
        self.survivor_pos = [0,0]
        self.supplies_collected = 0
        self.supplies_pos = []
        for supply in self.orig_supplies_pos:
            self.supplies_pos.append(supply)

    def generate_random_map(self, seed=None):
        # Random Target position
        random.seed(seed)
        self.door_pos = [
            random.randint(1, self.grid_rows-1),
            random.randint(1, self.grid_cols-1)
        ]

        self.zombies_pos = []

        for i in range(self.zombies_amount):
            position = self.random_pos()
            
            while (position == self.door_pos or position in self.zombies_pos):
                position = self.random_pos()

            self.zombies_pos.append(position)

        self.supplies_pos = []
        self.orig_supplies_pos = []
        for i in range(self.supplies_amount):
            position = self.random_pos()
            
            while (position == self.door_pos or position in self.zombies_pos or position in self.supplies_pos):
                position = self.random_pos()

            self.supplies_pos.append(position)
            self.orig_supplies_pos.append(position)

        self.supplies_collected = 0

        self.walls_pos = []
        for i in range(self.walls_amount):
            position = self.random_pos()
            
            while (position == self.door_pos or position in self.zombies_pos or position in self.supplies_pos
                   or position in self.walls_pos):
                position = self.random_pos()

            self.walls_pos.append(position)
        
        self.rocks_pos = []
        for i in range(self.rocks_amount):
            position = self.random_pos()
            
            while (position == self.door_pos or position in self.zombies_pos or position in self.supplies_pos
                   or position in self.walls_pos or position in self.rocks_pos):
                position = self.random_pos()

            self.rocks_pos.append(position)

    def random_pos(self):
        position = [
            random.randint(1, self.grid_rows-1),
            random.randint(1, self.grid_cols-1)
        ]

        return position

    def perform_action(self, survivor_action:SurvivorAction) -> int:
        self.last_action = survivor_action

        last_position = [self.survivor_pos[0], self.survivor_pos[1]]

        # Move Robot to the next cell
        if survivor_action == SurvivorAction.LEFT:
            if self.survivor_pos[1]>0:
                self.survivor_pos[1]-=1
        elif survivor_action == SurvivorAction.RIGHT:
            if self.survivor_pos[1]<self.grid_cols-1:
                self.survivor_pos[1]+=1
        elif survivor_action == SurvivorAction.UP:
            if self.survivor_pos[0]>0:
                self.survivor_pos[0]-=1
        elif survivor_action == SurvivorAction.DOWN:
            if self.survivor_pos[0]<self.grid_rows-1:
                self.survivor_pos[0]+=1

        # Return true if Robot reaches Target
        if (self.survivor_pos == self.door_pos):
            return GridTile.DOOR.value
        elif (self.survivor_pos in self.zombies_pos):
            return GridTile.ZOMBIE.value
        elif (self.survivor_pos in self.supplies_pos):
            self.remove_supply(self.survivor_pos)
            self.supplies_collected += 1
            return GridTile.SUPPLY.value
        elif (self.survivor_pos in self.walls_pos):
            self.survivor_pos = last_position
            return GridTile.WALL.value
        elif (self.survivor_pos in self.rocks_pos):
            self.survivor_pos = last_position
            return GridTile.ROCK.value
        
        return GridTile._FLOOR.value

    def render(self):
        self._process_events()

        # clear to white background, otherwise text with varying length will leave behind prior rendered portions
        self.window_surface.fill((255,255,255))

        # Print current state on console
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                
                # Draw floor
                pos = (c * self.cell_width, r * self.cell_height)
                self.window_surface.blit(self.floor_img, pos)

                if([r,c] == self.door_pos):
                    # Draw target
                    self.window_surface.blit(self.door_img, pos)

                if([r,c] == self.survivor_pos):
                    # Draw robot
                    self.window_surface.blit(self.survivor_img, pos)

                if([r,c] in self.zombies_pos):
                    self.window_surface.blit(self.zombie_img, pos)
                
                if([r,c] in self.supplies_pos):
                    self.window_surface.blit(self.supply_img, pos)
                
                if([r,c] in self.walls_pos):
                    self.window_surface.blit(self.wall_img, pos)
                
                if([r,c] in self.rocks_pos):
                    self.window_surface.blit(self.rock_img, pos)

                
        text_img = self.action_font.render(f'Action: {self.last_action}', True, (0,0,0), (255,255,255))
        text_pos = (0, self.window_size[1] - self.action_info_height)
        self.window_surface.blit(text_img, text_pos)       

        pygame.display.update()
                
        # Limit frames per second
        self.clock.tick(self.fps)  

    def _process_events(self):
        # Process user events, key presses
        for event in pygame.event.get():
            # User clicked on X at the top right corner of window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if(event.type == pygame.KEYDOWN):
                # User hit escape
                if(event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

    def remove_supply(self, pos):
        self.supplies_pos.remove(pos)