import pygame as pg
from pygame.locals import *
import sys
import math
import random

pg.init()
# Setting up colour objects
colours = {
    'BLUE': (0, 100, 200),
    'LIGHTBLUE': '#b4c2cf',
    'RED' : (225, 25, 25),
    'GREEN': (0, 255, 0),
    'BLACK': (60, 60, 60),
    'WHITE': (255, 255, 255),
    'GREY1': '#cccccc',
    'GREY2': '#c1c1c1',
    'GREY3': '#d9d9d9'
}

screen_x = 1000
screen_y = 800

num_squares = 2500
num_squares = int(round(math.sqrt(num_squares))**2)
delta = int(screen_x/int(math.sqrt(num_squares)))
settings_row_size = 4 # size in number of grid lines
num_lines_x = int(math.sqrt(num_squares) + 2)
num_lines_y = int((screen_y/delta) - settings_row_size)
squares = []
all_vertices = []
buttons = []

button_params = {
    'go': {
            'width':200,
            'height':66,
            'text_pos':(460,730),
            'text': 'START'
        },
    'reset': {
            'width':200,
            'height':66,
            'text_pos':(840,730),
            'text': 'RESET'
    },
    'pause': {
            'width':200,
            'height':66,
            'text_pos':(75,730),
            'text': 'PAUSE'
    }
}
button_params['go']['top_left_x'] = (screen_x/2) - 0.5*button_params['go']['width']
button_params['go']['top_left_y'] = (screen_y + ((screen_y/delta) - settings_row_size-1)*delta)/2 - button_params['go']['height']/2
button_params['reset']['top_left_x'] = screen_x - button_params['reset']['width'] - 20
button_params['reset']['top_left_y'] = (screen_y + ((screen_y/delta) - settings_row_size-1)*delta)/2 - button_params['reset']['height']/2
button_params['pause']['top_left_x'] = 20
button_params['pause']['top_left_y'] = (screen_y + ((screen_y/delta) - settings_row_size-1)*delta)/2 - button_params['pause']['height']/2

displaysurface = pg.display.set_mode((screen_x,screen_y))
displaysurface.fill(colours['GREY1'])
pg.display.set_caption("Conway's Game of Life")

class button():
    def __init__(self,name):
        self.name = name
        self.position = (button_params[self.name]['top_left_x'], button_params[self.name]['top_left_y'], button_params[self.name]['top_left_x'] + button_params[self.name]['width'], button_params[self.name]['top_left_y'] + button_params[self.name]['height'])
        return

    def draw_button(self,fill_col):
        pg.draw.rect(displaysurface, colours[fill_col], 
        pg.Rect(
            (
                button_params[self.name]['top_left_x'] + 1,
                button_params[self.name]['top_left_y'] + 1
            ), 
            (
                button_params[self.name]['width'] - 1,
                button_params[self.name]['height'] - 1
            )), width=0, border_top_left_radius=8, border_top_right_radius=8, border_bottom_left_radius=8, border_bottom_right_radius=8)
        pg.draw.rect(displaysurface, colours['BLUE'],
        pg.Rect(
            (
                button_params[self.name]['top_left_x'],
                button_params[self.name]['top_left_y']
            ), 
            (
                button_params[self.name]['width'],
                button_params[self.name]['height']
            )), width=3, border_top_left_radius=8, border_top_right_radius=8, border_bottom_left_radius=8, border_bottom_right_radius=8)
        self.font = pg.font.SysFont('Arial', 30)
        text_pos = button_params[self.name]['text_pos']
        displaysurface.blit(self.font.render(button_params[self.name]['text'],True, colours['RED']), text_pos)
        return

    def check_button_clicked(self,click_pos):
        x = click_pos[0]
        y = click_pos[1]
        if button_params[self.name]['top_left_x'] <= x <= button_params[self.name]['top_left_x'] + button_params[self.name]['width']:
            if button_params[self.name]['top_left_y'] <= y <= button_params[self.name]['top_left_y'] + button_params[self.name]['height']:
                return True
        return False

class cell():
    def __init__(self,position,alive):
        self.is_alive = alive
        self.position = position
        self.grid = (int(position[0]/delta), int(position[1]/delta))
        self.x = self.grid[0]
        self.y = self.grid[1]
        self.neighbours = [
            (self.x - 1, self.y - 1),
            (self.x, self.y - 1),
            (self.x + 1, self.y - 1),
            (self.x - 1, self.y),
            (self.x + 1, self.y),
            (self.x - 1, self.y + 1),
            (self.x, self.y + 1),
            (self.x + 1, self.y + 1)
        ]
        out = self.check_if_out_of_screen_borders()
        if not out:
            self.draw_alive_rect(delta)
        return

    def draw_alive_rect(self,delta):
        vertex = [self.position[i] + 1 for i in range(2)]
        return pg.draw.rect(displaysurface,colours['RED'],pg.Rect(vertex,(delta-1,delta-1)))
    
    def draw_dead_rect(self,delta):
        vertex = [self.position[i] + 1 for i in range(2)]
        return pg.draw.rect(displaysurface,colours['GREY1'],pg.Rect(vertex,(delta-1,delta-1)))
    
    def check_if_out_of_screen_borders(self):
        min_x, max_x, min_y, max_y = (0, screen_x, 0, (num_lines_y-1)*delta)
        if self.position[0] < min_x or self.position[0] > max_x or self.position[1] < min_y or self.position[1] >= max_y:
            return True
        else:
            return False
        
    def check_if_out_of_bounds(self):
        min_, max_ = (0-10*delta, screen_x + 10*delta)
        if self.position[0] < min_ or self.position[0] > max_ or self.position[1] < min_ or self.position[1] > max_:
            return True
        else:
            return False
       
    def update_state(self,neighbours,all_vertices):
        out = self.check_if_out_of_bounds()
        if out:
            self.is_alive = False
            return
        matches = set(all_vertices) & set(neighbours)
        if len(matches) == 2 or len(matches) == 3:
            self.is_alive = True
        else:
            self.is_alive = False
        return 

# cell presets
def random_pattern():
    for i in range(num_alive):
        rand_x = random.randint(0,int((screen_x/delta) - 1))
        rand_y = random.randint(0,int((screen_y/delta - settings_row_size - 2)))
        x_coord = rand_x * delta
        y_coord = rand_y * delta
        vertex = (rand_x,rand_y)
        vertex_coords = (x_coord,y_coord)

    return vertex, vertex_coords

def glider(j):
    coords_ = [(6,4),(7,5),(7,6),(6,6),(5,6)]
    coords = [(i[0]*delta,i[1]*delta) for i in coords_]
    return coords_[j], coords[j]

def george_test(j):
    coords_ = [
        (23,11), (23,12), (23,13), (24,13), (25,13), (25,14),
        (26,19), (26,18), (26,17), (25,17), (24,17), (24,16),
    ]
    for i in range(14):
        coords_.append((18+i,15))
    coords = [(i[0]*delta,i[1]*delta) for i in coords_]
    return coords_[j], coords[j]

def glider_gun(j):
    coords = [
        (60, 160), (60, 180), (80, 160), (80, 180), (260, 160), (260, 180), (260, 200), (280, 220), (300, 240), (320, 240), (360, 220), (380, 200), (380, 180), 
        (380, 160), (400, 180), (360, 140), (340, 180), (280, 140), (300, 120), (320, 120), (460, 160), (460, 140), (460, 120), (480, 120), (480, 140), (480, 160), 
        (500, 100), (500, 180), (540, 80), (540, 100), (540, 180), (540, 200), (740, 120), (740, 140), (760, 140), (760, 120)
    ]
    return None, coords[j]

def nice_symmetry(j):
    coords = [
        (460, 200), (460, 220), (460, 240), (460, 260), (460, 280), (460, 300), (480, 300), (500, 300), (500, 280), (480, 260), (480, 280), (500, 260), (480, 220), 
        (480, 240), (500, 220), (500, 240), (500, 200), (480, 200), (480, 320), (480, 340), (440, 360), (460, 360), (480, 360), (500, 360), (520, 360), (520, 380), 
        (520, 400), (520, 420), (520, 440), (500, 440), (480, 440), (460, 440), (440, 440), (440, 420), (440, 400), (440, 380), (540, 340), (540, 400), (540, 460), 
        (420, 400), (420, 340), (420, 460), (460, 460), (460, 480), (460, 500), (480, 500), (500, 500), (500, 480), (480, 480), (480, 460), (500, 460)
    ]
    return None, coords[j]

# cell operations
def update_squares_list(squares_list,cells_to_kill,all_neighbours):
    """ remove dead cells from the list of objects, add revived cells """
    squares_grids = []

    for square in squares_list:
        if square.grid in cells_to_kill:
            out = square.check_if_out_of_screen_borders()
            if not out:
                square.draw_dead_rect(delta)
        else:
            squares_grids.append(square.grid)

    potential_revived_cells = {i:all_neighbours.count(i) for i in all_neighbours}
    for key in potential_revived_cells.keys():
        if potential_revived_cells[key] == 3:
            coords = (int(key[0]*delta), int(key[1]*delta))
            square = cell(position=coords,alive=True)
            squares_grids.append(square.grid)

    squares_final_grids = []
    [squares_final_grids.append(grid) for grid in squares_grids if grid not in squares_final_grids]
    squares_final = []
    for grid_coords in squares_final_grids:
        coords = (int(grid_coords[0]*delta), int(grid_coords[1]*delta))
        squares_final.append(cell(position=coords,alive=True))

    return squares_final

def create_cell_upon_click(click_pos):
    x = int(click_pos[0]/delta)*delta
    y = int(click_pos[1]/delta)*delta
    already_clicked = False
    for i, square in enumerate(squares):
        if square.position == (x,y):
            squares.pop(i)
            square.draw_dead_rect(delta)
            already_clicked = True
    if not already_clicked:
        square = cell(position=(x,y),alive=True)
        square.draw_alive_rect(delta)
        squares.append(square)

# grid setup
def draw_grid_lines(num_lines_x,num_lines_y):
    x = 0 
    y = 0
    for i in range(int(num_lines_x)):
        pg.draw.line(displaysurface,colours['BLACK'],(x,0),(x,(num_lines_y-1)*delta))
        x += delta
    for i in range(int(num_lines_y)):
        pg.draw.line(displaysurface,colours['BLACK'],(0,y),(screen_x,y))
        y += delta
    return

# button panel setup
def draw_button_panel(num_lines_y,screen_x,settings_row_size):
    pg.draw.rect(displaysurface, colours['LIGHTBLUE'], 
        pg.Rect(
            (0, (num_lines_y-1)*delta + 1),
            (screen_x, (settings_row_size+1)*delta)
        )
    )
    return

j = 0
go = 0
pattern = nice_symmetry
if pattern == glider:
    num_alive = 5
elif pattern == george_test:
    num_alive = 26
elif pattern == random_pattern:
    num_alive = 200
elif pattern == glider_gun:
    num_alive = 36
elif pattern == nice_symmetry:
    num_alive = 51
else:
    num_alive = 0

# draw elements on screen
draw_grid_lines(num_lines_x,num_lines_y)
# draw button panel
draw_button_panel(num_lines_y,screen_x,settings_row_size)
# draw buttons
btn_names = ['go', 'reset', 'pause']
for name in btn_names:
    btn = button(name)
    btn.draw_button(fill_col='GREY3')
    buttons.append(btn)
test = []
# game code
while True:
    clock = pg.time.Clock()
    clock.tick(60)
    for btn in buttons:
        if btn.position[0] <= pg.mouse.get_pos()[0] <= btn.position[2]:
            if btn.position[1] <= pg.mouse.get_pos()[1] <= btn.position[3]:
                btn.draw_button(fill_col='GREY1')
        else:
            btn.draw_button(fill_col='GREY3')

    # dynamic cell creation
    reset = False
    for event in pg.event.get():
        if event.type == MOUSEBUTTONDOWN:
            click_pos = event.pos
            if click_pos[1] <= (num_lines_y-1)*delta and not reset: # clicked in grid region
                test.append(click_pos)
                create_cell_upon_click(click_pos)
            else: # clicked in button region
                if not reset:
                    for btn in buttons:
                        if btn.check_button_clicked(click_pos):
                            if btn.name == 'go':
                                go = 1
                            elif btn.name == 'reset':
                                for square in squares:
                                    if square.is_alive:
                                        out = square.check_if_out_of_screen_borders()
                                        if not out:
                                            square.draw_dead_rect(delta)
                                reset = True
                                squares = []
                                j = 0
                            elif btn.name == 'pause':
                                go = 0

        elif event.type == QUIT:
                pg.quit()
                sys.exit()
    
    # static cell creation
    while j < num_alive:
        if pattern == random_pattern:
            vertex, vertex_coords = pattern()
        else:
            vertex, vertex_coords = pattern(j)
        all_vertices.append(vertex)
        square = cell(position=vertex_coords,alive=True)
        squares.append(square)
        j += 1

    if go == 1:
        all_vertices = [x.grid for x in squares] # keep track of every grid position which is currently active
        cells_to_kill = []
        all_neighbours = []
        for square in squares:
            dead = square.update_state(square.neighbours,all_vertices)
            if not square.is_alive:
                cells_to_kill.append(square.grid)
            for n in square.neighbours:
                all_neighbours.append(n)

        squares = update_squares_list(squares,cells_to_kill,all_neighbours)

    pg.display.update()