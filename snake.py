#!/usr/bin/python3
import pygame, sys, random, glob, os
from pygame.math import Vector2
from pygame.transform import flip, rotate, scale


# original Snake created by Sara Martínez
#
# Snake Pi modifications by MS-potilas 2026
# Snake Pi made for RetroPie, but can be run also without it.

# name of the game for old style title screen
oldtitle = "Snake Pi"

cmdline = " " + (" ".join(sys.argv)) + " "
cmdline = cmdline.replace('‑', '-')  # non-breaking hyphen to hyphen


# FPS
FRAME_RATE = 30                     # more authentic than 60 fps?

# timeouts etc
SNAKE_UPDATE_MS = 180
GAMEOVER_TIMEOUT_MS = 12000
ENABLE_INPUT_AFTER_GAMEOVER_MS = 3000
PLAY_TITLE_MUSIC_AFTER_MS = 500

# Colors (R, G, B)
GREEN = (112, 142, 83)
TRUEGREEN = (0x6d, 0x8b, 0x50)      # green left after ghosting effect
BLACK = (0x1f, 0x22, 0x18)          # greenish LCD-black
LESSBLACK = (0x30, 0x35, 0x2A)      # something semi-odd for scrolltext

ANIMAL_FREQUENCY = 5                # normally 5
RETRO_BONUS_AFTER_SCORE = 500       # normally 500

MOBILE_PHONE_ANIMAL_INDEX = 10      # eating this plays nokia tune

FONT_SIZE = 34                      # score and animal timer
SCROLL_FONT_SIZE = 24

OFFSET = 80                         # border width
TOP_OFFSET = 40                     # additional top border

CELL_SIZE = 22                      # 22 compatible with both overlays

# 3310 play field
NUM_OF_CELLS_WIDTH = 29
NUM_OF_CELLS_HEIGHT = 19

# scroll text

scrolltext = '      Welcome to Snake Pi, a remake of the 1998 Nokia game "Snake II". Snake Pi was made specifically for RetroPie, hence the name. Thanks to Sara Martinez for the groundwork. Kind regards, MS-potilas, in 2026.    Feel free to copy and reuse my work.    High score is [HS].'

SCROLLTEXT_SPEED = 5

# overlay image size
OVERLAY_W = 1920
OVERLAY_H = 1080


# FLAG: original (old / first) Snake game (oldsnake = True), or newer Snake II (oldsnake = False)
# cmdline:  --old               : sets oldsnake True
#           --oldrandom         : includes old snake in random game and overlay selection
#                                 probability to get old tyle game is 20%
oldsnake = False

# User events
EV_SNAKE_UPDATE = pygame.USEREVENT + 1
EV_ENABLE_INPUT = pygame.USEREVENT + 2
EV_GAME_OVER_TIMEOUT = pygame.USEREVENT + 3
EV_PLAY_MUSIC = pygame.USEREVENT + 4

# change working dir to same as the script's
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# globals
tunename = ''
casename = ''
GAME_W = 100
GAME_H = 100
WINDOW_W = 1280
WINDOW_H = 720
OFFSET_X = 0
OFFSET_Y = 0
fullscreen = False
overlay = None
titleimage = None
GAME_SURFACE = None
IMG_NAMES = []
IMAGES = {}
FORMAT_IMAGES = {}

# don't know if this works on windows or mac
def is_windowing_system():
    if sys.platform == 'windows' or sys.platform == 'darwin': # windows or mac
        return True
    if os.environ.get('DISPLAY'):
        return True
    return False


# recycle next overlay and/or game style
# if --old is used, cycle between 5110 and 6110
# if --oldrandom is used, cycle between 5110, 6110, 7110, and 3310
# if neither --old nor --oldrandom is used, cycle between 7110 and 3310
def reinit_next_game():
    global oldsnake, cmdline, casename, fullscreen
    argv = []
    if fullscreen:
        argv.append('--fullscreen')
    else:
        argv.append('--windowed')
    if casename == '':
        argv.append('--nocase')
        if oldsnake:
            pass
        else:
            argv.append('--old')
    else:
        if '-old ' in cmdline:
            argv.append('--old')
            if '5110' in casename:
                argv.append('--6110')
            elif '6110' in casename:
                argv.append('--5110')
        elif '-oldrandom ' in cmdline or '5110' in casename or '6110' in casename:
            argv.append('--oldrandom')
            if '5110' in casename:
                argv.append('--6110')
            elif '6110' in casename:
                argv.append('--7110')
            elif '7110' in casename:
                argv.append('--3310')
            elif '3310' in casename:
                argv.append('--5110')
        else:
            if '7110' in casename:
                argv.append('--3310')
            elif '3310' in casename:
                argv.append('--7110')
    # new command line
    cmdline = " " + (" ".join(argv)) + " "     

# reinit globals according to command line options, (re)init pygame
def reinit_globals():
    global cmdline, oldsnake, OFFSET, CELL_SIZE, TOP_OFFSET, NUM_OF_CELLS_WIDTH, NUM_OF_CELLS_HEIGHT, SNAKE_UPDATE_MS, IMAGES, FORMAT_IMAGES, tunename, casename, GAME_SURFACE, titleimage, overlay, MAIN_SCREEN, OFFSET_X, OFFSET_Y, GAME_W, GAME_H, ANIMAL_FREQUENCY, RETRO_BONUS_AFTER_SCORE, GREEN, TRUEGREEN, fullscreen

    oldsnake = False

    # timeouts etc
    SNAKE_UPDATE_MS = 180
    GAMEOVER_TIMEOUT_MS = 12000

    ANIMAL_FREQUENCY = 5                # normally 5
    RETRO_BONUS_AFTER_SCORE = 500       # normally 500

    FONT_SIZE = 34                      # score and animal timer
    SCROLL_FONT_SIZE = 24

    OFFSET = 80                         # border width
    TOP_OFFSET = 40                     # additional top border

    CELL_SIZE = 22                      # 22 compatible with both overlays

    # 3310 play field
    NUM_OF_CELLS_WIDTH = 29
    NUM_OF_CELLS_HEIGHT = 19

    tunename = random.choice(glob.glob('sounds/nokia_tune*.wav'))


    if "-oldrandom " in cmdline:
        if random.randint(1, 5) == 1:       # old snake probability 20%
            oldsnake = True

    if "-7110 " in cmdline:
        casename = 'images/nokia_case7110.png'
        oldsnake = False
    elif "-3310 " in cmdline:
        casename = 'images/nokia_case3310.png'
        oldsnake = False
    elif "-nocase " in cmdline:
        casename = ''
    elif "-6110 " in cmdline:
        casename = 'images/nokia_oldcase6110.png'
        oldsnake = True
    elif "-5110 " in cmdline:
        casename = 'images/nokia_oldcase5110.png'
        oldsnake = True
    else:
        casename = random.choice(glob.glob('images/nokia_case*.png'))

    if "-old " in cmdline or oldsnake:
        oldsnake = True
        ANIMAL_FREQUENCY = 0                # no animals on first Snake
        NUM_OF_CELLS_WIDTH = 20
        NUM_OF_CELLS_HEIGHT = 13
        CELL_SIZE = 12                      # smaller cells
        TOP_OFFSET = 0                      # no score! no this is 0
        GREEN = (0x8d, 0xbd, 0x8d)          # different greens
        TRUEGREEN = (0x80, 0xb0, 0x82)  
        GAMEOVER_TIMEOUT_MS = 60000         # no rush to get to title screen
        tunename = 'sounds/nokia_tune.wav'  # no fancy stuff
        SNAKE_UPDATE_MS = 200

        RETRO_BONUS_AFTER_SCORE = 50 * 7    # after 50 orbs, otherwise too hard, not fun!
        
        # if no old nokia case overlay is selected, select one from the old case overlays
        if casename != '' and not 'oldcase' in casename:
            casename = random.choice(glob.glob('images/nokia_oldcase*.png'))


    if '7110' in casename:
        # 7110-optimized play field 
        NUM_OF_CELLS_WIDTH = 26
        NUM_OF_CELLS_HEIGHT = 21

    # play field is different, when no overlay (oxcept in old snake game)
    if casename == '':
        if not oldsnake:
            NUM_OF_CELLS_WIDTH = 30
            NUM_OF_CELLS_HEIGHT = 20
        else:
            CELL_SIZE = 18
            FONT_SIZE = 50          # title screen font
            SCROLL_FONT_SIZE = 32   # game over font

    # game area size
    GAME_W = 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_WIDTH
    GAME_H = TOP_OFFSET + 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_HEIGHT

    WINDOW_W = 1280
    WINDOW_H = 720

    if "-nocase " in cmdline:
        OFFSET = 50
        GAME_W = 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_WIDTH
        GAME_H = TOP_OFFSET + 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_HEIGHT
        WINDOW_W = GAME_W
        WINDOW_H = GAME_H



    pygame.quit()   # to reinit, call quit first
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    # init Pygame
    pygame.init()

    # get full screen size (for example 1920x1080 or 1280x720)
    display_info = pygame.display.Info()
    FULL_SCREEN_W = display_info.current_w
    FULL_SCREEN_H = display_info.current_h

    # calculate game area offset
    OFFSET_X = (OVERLAY_W - GAME_W) // 2
    OFFSET_Y = (OVERLAY_H - GAME_H) // 2


    fullscreen = False

    if (is_windowing_system() and not "-fullscreen " in cmdline) or "-windowed " in cmdline:
        # create a window (under X or Wayland, for example)
        MAIN_SCREEN = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE )
        pygame.display.set_caption("Snake Pi")
    else:
        # create full screen display 
        MAIN_SCREEN = pygame.display.set_mode((FULL_SCREEN_W, FULL_SCREEN_H), pygame.FULLSCREEN | pygame.NOFRAME )
        pygame.mouse.set_visible(False)         # hide mouse cursor
        fullscreen = True



    pygame.key.set_repeat(50, SNAKE_UPDATE_MS)

    overlay = None
    try:
        # load overlay image (nokia_case.png)
        # convert_alpha() makes image faster to draw while preserving alpha channel
        overlay = pygame.image.load(casename).convert_alpha()
    except:
        #print("Overlay image could not be loaded, continuing without.")
        pass

    titleimage = pygame.image.load("images/snake_pi.png").convert_alpha()
    #titleimage =  scale(titleimage, (titleimage.get_width() * 1.2, titleimage.get_height() * 1.2))


    # create virtual surface for the game itself
    GAME_SURFACE = pygame.Surface((GAME_W, GAME_H))


    IMG_NAMES = ["food", "head", "body", "tail", "turn", "fhead", "fbody", "ftail", "fturn", "animal1", "animal2", "animal3", "animal4", "animal5", "animal6", "animal7", "animal8", "animal9", "animal10"]
    IMAGES = { name: pygame.image.load("images/" + "{}.png".format(name)).convert_alpha() for name in IMG_NAMES}

    if oldsnake:
        IMAGES['head'] = snakeimg = pygame.image.load("images/oldbody.png").convert_alpha()
        IMAGES['food'] = pygame.image.load("images/oldfood.png").convert_alpha()
       
    FORMAT_IMAGES = {
        "food": scale(IMAGES["food"], (CELL_SIZE, CELL_SIZE)),
        "head_R": scale(IMAGES["head"], (CELL_SIZE, CELL_SIZE)),
        "head_L": scale(flip(IMAGES["head"], True, False), (CELL_SIZE, CELL_SIZE)),
        "head_U": scale(rotate(IMAGES["head"], 90), (CELL_SIZE, CELL_SIZE)),
        "head_D": scale(flip(rotate(IMAGES["head"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "body_R": scale(IMAGES["body"], (CELL_SIZE, CELL_SIZE)),
        "body_L": scale(flip(IMAGES["body"], True, False), (CELL_SIZE, CELL_SIZE)),
        "body_U": scale(rotate(IMAGES["body"], 90), (CELL_SIZE, CELL_SIZE)),
        "body_D": scale(flip(rotate(IMAGES["body"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "tail_R": scale(IMAGES["tail"], (CELL_SIZE, CELL_SIZE)),
        "tail_L": scale(flip(IMAGES["tail"], True, False), (CELL_SIZE, CELL_SIZE)),
        "tail_U": scale(rotate(IMAGES["tail"], 90), (CELL_SIZE, CELL_SIZE)),
        "tail_D": scale(flip(rotate(IMAGES["tail"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "turn_R": scale(IMAGES["turn"], (CELL_SIZE, CELL_SIZE)),
        "turn_L": scale(flip(IMAGES["turn"], True, False), (CELL_SIZE, CELL_SIZE)),
        "turn_U": scale(rotate(IMAGES["turn"], 90), (CELL_SIZE, CELL_SIZE)),
        "turn_D": scale(rotate(IMAGES["turn"], 180), (CELL_SIZE, CELL_SIZE)),
        "fhead_R": scale(IMAGES["fhead"], (CELL_SIZE, CELL_SIZE)),
        "fhead_L": scale(flip(IMAGES["fhead"], True, False), (CELL_SIZE, CELL_SIZE)),
        "fhead_U": scale(rotate(IMAGES["fhead"], 90), (CELL_SIZE, CELL_SIZE)),
        "fhead_D": scale(flip(rotate(IMAGES["fhead"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "fbody_R": scale(IMAGES["fbody"], (CELL_SIZE, CELL_SIZE)),
        "fbody_L": scale(flip(IMAGES["fbody"], True, False), (CELL_SIZE, CELL_SIZE)),
        "fbody_U": scale(rotate(IMAGES["fbody"], 90), (CELL_SIZE, CELL_SIZE)),
        "fbody_D": scale(flip(rotate(IMAGES["fbody"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "ftail_R": scale(IMAGES["ftail"], (CELL_SIZE, CELL_SIZE)),
        "ftail_L": scale(flip(IMAGES["ftail"], True, False), (CELL_SIZE, CELL_SIZE)),
        "ftail_U": scale(rotate(IMAGES["ftail"], 90), (CELL_SIZE, CELL_SIZE)),
        "ftail_D": scale(flip(rotate(IMAGES["ftail"], 270), True, False), (CELL_SIZE, CELL_SIZE)),
        "fturn_R": scale(IMAGES["fturn"], (CELL_SIZE, CELL_SIZE)),
        "fturn_L": scale(flip(IMAGES["fturn"], True, False), (CELL_SIZE, CELL_SIZE)),
        "fturn_U": scale(rotate(IMAGES["fturn"], 90), (CELL_SIZE, CELL_SIZE)),
        "fturn_D": scale(rotate(IMAGES["fturn"], 180), (CELL_SIZE, CELL_SIZE)),
    }

    if oldsnake:
        # in old snake, all snake parts are the same, without flips or rotations!
        lst = ["head_R", "head_L", "head_U", "head_D",
               "body_R", "body_L", "body_U", "body_D",
               "turn_R", "turn_L", "turn_U", "turn_D",
               "tail_R", "tail_L", "tail_U", "tail_D",
               "fhead_R", "fhead_L", "fhead_U", "fhead_D",
               "fbody_R", "fbody_L", "fbody_U", "fbody_D",
               "fturn_R", "fturn_L", "fturn_U", "fturn_D",
               "ftail_R", "ftail_L", "ftail_U", "ftail_D"]
        for i in lst:
            FORMAT_IMAGES[i] = FORMAT_IMAGES['head_R']

    pygame.time.set_timer(EV_SNAKE_UPDATE, SNAKE_UPDATE_MS)
    pygame.time.set_timer(EV_PLAY_MUSIC, PLAY_TITLE_MUSIC_AFTER_MS)


# quick and dirty class for reading joysticks
class Joystick:
    def __init__(self):
        self.move = Vector2(0,0)
        self.buttons = []
        pygame.joystick.init()
        self.numsticks = pygame.joystick.get_count()
        # stick names can be used for detecting stick properties
        self.sticknames = []
        for i in range(self.numsticks):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            name = joystick.get_name()
            self.sticknames.append(name)
        
    def get_joy(self):
        # Get count of joysticks (it may have changed? but apparently not)
        joystick_count = pygame.joystick.get_count()
        self.move.x = 0
        self.move.y = 0
        self.buttons = []
        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            # get axes
            axes = joystick.get_numaxes()
            for ii in range(axes):
                axis = joystick.get_axis(ii)
                if ii == 0:
                    if axis < -0.5:
                        self.move.x = -1
                    if axis > 0.5:
                        self.move.x = 1
                if ii == 1:
                    if axis < -0.5:
                        self.move.y = -1
                    if axis > 0.5:
                        self.move.y = 1
            # get buttons
            numbuttons = joystick.get_numbuttons()
            for i in range(numbuttons):
                buttonval = joystick.get_button(i)
                if buttonval and not i in self.buttons:
                    self.buttons.append(i)


class Snake:
    def __init__(self, thegame):
        self.body = []
        self.thegame = thegame
        self.body_directions = []
        self.body_foods = []
        self.direction = Vector2(-1, -1)
        self.current_direction = self.direction
        self.reset()
        self.add_block = False
        self.eat_sound = pygame.mixer.Sound("sounds/eat.wav")
        self.eat_phone_sound = pygame.mixer.Sound("sounds/nokia_tune.wav")
        self.eat_phone_sound.set_volume(0.5)
        self.gameover_sound = pygame.mixer.Sound("sounds/game_over.wav")
        self.highscore_sound = pygame.mixer.Sound("sounds/game_over_high.wav")

    def get_direction_name(self):
        if self.current_direction == Vector2(-1, 0):
            return "L"
        elif self.current_direction == Vector2(0, -1):
            return "U"
        elif self.current_direction == Vector2(0, 1):
            return "D"
        else:
            return "R"

    def get_block_image(self, index):
        pre = 'f' if self.body_foods[index] else ''
        if index == 0:
            next_position = self.body[0] + self.current_direction
            # is food in next position? if, open the mouth
            if self.thegame.check_position_for_food(next_position):
                pre = 'f'
            return FORMAT_IMAGES[pre+"head_" + self.get_direction_name()]
        else:
            direction = self.body_directions[index]
            prev_direction = self.body_directions[index - 1]
            if index == len(self.body) - 1:
                return FORMAT_IMAGES[pre+"tail_" + prev_direction]
            elif direction != prev_direction:
                if (prev_direction == "R" and direction == "D") or (prev_direction == "U" and direction == "L"):
                    return FORMAT_IMAGES[pre+"turn_U"]
                elif (prev_direction == "L" and direction == "U") or (prev_direction == "D" and direction == "R"):
                    return FORMAT_IMAGES[pre+"turn_L"]
                elif (prev_direction == "R" and direction == "U") or (prev_direction == "D" and direction == "L"):
                    return FORMAT_IMAGES[pre+"turn_R"]
                else:
                    return FORMAT_IMAGES[pre+"turn_D"]
            else:
                return FORMAT_IMAGES[pre+"body_" + prev_direction]
    
    def draw(self):
        for index, block in enumerate(self.body):
            snake_surface = self.get_block_image(index)
            block_rect = pygame.Rect(OFFSET + block.x * CELL_SIZE, TOP_OFFSET + OFFSET + block.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            GAME_SURFACE.blit(snake_surface, block_rect)

    def update(self):
        self.current_direction = self.direction
        self.body.insert(0, self.body[0] + self.direction)
        self.body_directions.insert(0, self.get_direction_name())
        self.body_foods.insert(0, 0)

    def post_update(self):
        if self.add_block == True:
            self.add_block = False
        else:
            self.body = self.body[:-1]
            self.body_directions = self.body_directions[:-1]
            self.body_foods = self.body_foods[:-1]


    def reset(self):
        y = NUM_OF_CELLS_HEIGHT // 2 - 2 
        self.body = [Vector2(5, y), Vector2(4, y), Vector2(3, y)]
        self.body_directions = ["R", "R", "R"]
        self.body_foods = [0, 0, 0]
        self.direction = Vector2(1, 0)
        self.current_direction = self.direction


class Food:
    def __init__(self, snake_body):
        self.position = self.create_random_pos(snake_body)
        self.superfood = False

    def draw(self):
        if not self.superfood:
            food_surface = FORMAT_IMAGES["food"]
        else:
            food_surface = scale(IMAGES["animal9"], (CELL_SIZE, CELL_SIZE))
        food_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE, TOP_OFFSET + OFFSET + self.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        GAME_SURFACE.blit(food_surface, food_rect)

    def get_random_cell(self):
        x = random.randint(0, NUM_OF_CELLS_WIDTH - 1)
        y = random.randint(0, NUM_OF_CELLS_HEIGHT - 1)
        return Vector2(x, y)

    def create_random_pos(self, snake_body):
        position = self.get_random_cell()
        while position in snake_body:
            position = self.get_random_cell()
        return position


class Animal:
    def __init__(self, snake_body, food_position, active_timer):
        self.position = self.create_random_pos(snake_body, food_position)
        self.image = None
        self.bigimage = None
        self.phone_animal = False
        self.create_random_image()
    
    def create_random_image(self, extended = False):
        random_number = random.randint(1, 10 if extended else 6)
        if random_number  == MOBILE_PHONE_ANIMAL_INDEX:
            self.phone_animal = True
        else:
            self.phone_animal = False
        self.image = scale(IMAGES["animal" + str(random_number)], (CELL_SIZE, CELL_SIZE))
        self.bigimage =  scale(IMAGES["animal" + str(random_number)], (round(CELL_SIZE*1.5), round(CELL_SIZE*1.5))) 
    
    def draw(self, active_timer):
        if active_timer:
            animal_surface = self.image
            animal_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE, TOP_OFFSET + OFFSET + self.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            GAME_SURFACE.blit(animal_surface, animal_rect)
    
    def get_random_cell(self):
        x = random.randint(0, NUM_OF_CELLS_WIDTH - 1)
        y = random.randint(0, NUM_OF_CELLS_HEIGHT - 1)
        return Vector2(x, y)

    def create_random_pos(self, snake_body, food_position):
        position = self.get_random_cell()
        while position in snake_body or position == food_position:
            position = self.get_random_cell()
        return position    


class Game:
    def __init__(self, oldsnake):
        self.clock = pygame.time.Clock()
        self.snake = Snake(self)
        self.food = Food(self.snake.body)
        self.oldsnake = oldsnake
        self.status = "PRE_GAME"
        self.score = 0
        self.food_counter = 0
        self.num_of_frames = 0
        self.active_timer = False
        self.animal = Animal(self.snake.body, self.food.position, self.active_timer)
        self.joysticks = Joystick()
        # select random nokia tune for title screen
        self.nokia_tune = pygame.mixer.Sound(tunename)
        self.score_font = pygame.font.Font("fonts/nokiafc22.ttf", FONT_SIZE)
        self.input_active = True

        self.scroll_font = pygame.font.Font("fonts/nokiafc22.ttf", SCROLL_FONT_SIZE)
        
        self.gameover_text = ''
        self.high_score = 0
        self.load_highscore()
        self.scroll_text = None
        self.scroll_rect = None
        self.update_scrolltext()
        
        self.ghost_layer = pygame.Surface((GAME_W, GAME_H))
        self.ghost_layer.fill(TRUEGREEN)
    
    def load_highscore(self):
        try:
            with open('.highscore', "r") as f:
                self.high_score = int(f.read())
        except:
            pass
            
    def save_highscore(self):
        try:
            with open('.highscore', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def update_scrolltext(self):
        scrolltext_hs = scrolltext.replace('[HS]', str(self.high_score))
        self.scroll_text = self.scroll_font.render(scrolltext_hs, True, LESSBLACK)
        self.scroll_rect = self.scroll_text.get_rect(left=GAME_W, top=GAME_H - OFFSET - FONT_SIZE)
        
        
    def draw(self):
        width = 3 if self.oldsnake else 5
        pygame.draw.rect(GAME_SURFACE, BLACK, (OFFSET - 5, TOP_OFFSET + OFFSET - 5, CELL_SIZE * NUM_OF_CELLS_WIDTH + 10, CELL_SIZE * NUM_OF_CELLS_HEIGHT + 10), width)
        if not self.oldsnake:
            pygame.draw.line(GAME_SURFACE, BLACK, (OFFSET - 5, TOP_OFFSET + OFFSET - 15), (OFFSET + 5 + CELL_SIZE * NUM_OF_CELLS_WIDTH, TOP_OFFSET + OFFSET - 15), width)
        self.snake.draw()
        self.food.draw()
        self.animal.draw(self.active_timer)

    def update(self):
        if self.status == "PLAYING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_animal()
            self.check_collision_with_edges()
            self.check_collision_with_tail()
            self.snake.post_update()

    def update_food_counter(self):
        if not self.active_timer:
            self.food_counter += 1
            if ANIMAL_FREQUENCY and self.food_counter >= ANIMAL_FREQUENCY: 
                # new random position, because snake and food have moved
                self.animal.position = self.animal.create_random_pos(self.snake.body, self.food.position)
                self.active_timer = True

    def check_collision_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.snake.body_foods[0] = 1
            self.snake.eat_sound.play()
            self.food.position = self.food.create_random_pos(self.snake.body)
            self.snake.add_block = True
            self.score += 7
            self.update_food_counter()
            # different retro bonus in old snake
            if self.oldsnake and self.score > RETRO_BONUS_AFTER_SCORE:
                self.food.superfood = True

    def reset_timer(self):
        self.food_counter = 0
        self.num_of_frames = 0
        self.active_timer = False
        self.animal.create_random_image(self.score > RETRO_BONUS_AFTER_SCORE)

    def check_position_for_food(self, position):
        if (self.active_timer and position == self.animal.position) or position == self.food.position:
            return True
        else:
            return False

    def check_collision_with_animal(self):
        if self.snake.body[0] == self.animal.position and self.active_timer:
            self.snake.body_foods[0] = 1
            self.snake.eat_sound.play()
            if self.animal.phone_animal:
                self.snake.eat_phone_sound.play()
            self.animal.position = self.animal.create_random_pos(self.snake.body, self.food.position)
            self.snake.add_block = True
            self.score += 40
            self.reset_timer()

    def check_collision_with_edges(self):
        if self.snake.body[0].x == NUM_OF_CELLS_WIDTH or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == NUM_OF_CELLS_HEIGHT or self.snake.body[0].y == -1:
            self.game_over()

    def check_collision_with_tail(self):
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()

    def game_over(self):
        self.snake.add_block = True
        self.snake.body.pop(0)
        self.snake.body_directions.pop(0)
        self.snake.body_foods.pop(0)
        
        if self.score > self.high_score and not self.oldsnake:
            self.snake.highscore_sound.play()
            self.high_score = self.score
            self.save_highscore()
            self.gameover_text = '-+* HIGH SCORE! *+-'
        else:
            self.snake.gameover_sound.play()
            self.gameover_text = 'GAME OVER'
            
        self.status = "GAME_OVER"
        pygame.time.set_timer(EV_GAME_OVER_TIMEOUT, GAMEOVER_TIMEOUT_MS)
        pygame.time.set_timer(EV_ENABLE_INPUT, ENABLE_INPUT_AFTER_GAMEOVER_MS)
        self.input_active = False

    def play(self):
        self.food.superfood = False
        self.gameover_text = ''
        self.snake.reset()
        self.food.position = self.food.create_random_pos(self.snake.body)
        self.score = 0
        self.status = "PLAYING"
        self.reset_timer()


    def QUIT(self):
        pygame.quit()
        sys.exit()


    def run(self):
        while True:                
            for ev in pygame.event.get():
                if ev.type == EV_ENABLE_INPUT:
                    pygame.time.set_timer(EV_ENABLE_INPUT, 0)
                    self.input_active = True
                if ev.type == EV_GAME_OVER_TIMEOUT:
                    pygame.time.set_timer(EV_GAME_OVER_TIMEOUT, 0)
                    if self.status == 'GAME_OVER':
                        self.status = "PRE_GAME"
                        self.update_scrolltext()
                        self.reset_timer()
                if ev.type == EV_PLAY_MUSIC:
                    pygame.time.set_timer(EV_PLAY_MUSIC, 0)
                    self.nokia_tune.play()
                if ev.type == pygame.QUIT:
                    self.QUIT()
                if ev.type == pygame.KEYDOWN:
                    # 0 / O / N: cycle next overlay
                    if ev.key == pygame.K_0 or ev.key == pygame.K_o or ev.key == pygame.K_n:
                        return
                    # ESCAPE and Q key quits
                    if ev.key == pygame.K_ESCAPE or ev.key == pygame.K_q:
                        self.QUIT()
                    # ctrl+C and ctrl+ENTER (RetroPie) quits
                    if (ev.key == pygame.K_c or ev.key == pygame.K_RETURN) and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.QUIT()
                if ev.type == EV_SNAKE_UPDATE:
                    self.joysticks.get_joy()
                    if self.status == 'PLAYING':
                        if self.joysticks.move.y and self.snake.current_direction.x:
                            self.snake.direction = Vector2(0, self.joysticks.move.y)
                        elif self.joysticks.move.x and self.snake.current_direction.y:
                            self.snake.direction = Vector2(self.joysticks.move.x , 0)
                    if len(self.joysticks.buttons):
                        # upper buttons (including start & select, hopefully):
                        for j in range(6,15):
                            if j in self.joysticks.buttons:
                                self.QUIT()
                    if (self.status == "PRE_GAME" or (self.status == "GAME_OVER" and self.input_active)) and (len(self.joysticks.buttons) or self.joysticks.move.y or self.joysticks.move.x):
                        self.play()
                    self.update()
                if ev.type == pygame.KEYDOWN:
                    total_seconds = 9 - (self.num_of_frames // FRAME_RATE)
                    if self.status == "PRE_GAME" or (self.status == "GAME_OVER" and self.input_active):
                        if ev.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                            self.play()
                    if self.status == 'PLAYING':
                        if (ev.key == pygame.K_UP or ev.key == pygame.K_KP8) and self.snake.current_direction.x:
                            self.snake.direction = Vector2(0, -1)
                        if (ev.key == pygame.K_DOWN or ev.key == pygame.K_KP2) and self.snake.current_direction.x:
                            self.snake.direction = Vector2(0, 1)
                        if (ev.key == pygame.K_LEFT or ev.key == pygame.K_KP4) and self.snake.current_direction.y:
                            self.snake.direction = Vector2(-1, 0)
                        if (ev.key == pygame.K_RIGHT or ev.key == pygame.K_KP6) and self.snake.current_direction.y:
                            self.snake.direction = Vector2(1, 0)
                        

            if self.status == 'PRE_GAME':
                # title screen
                GAME_SURFACE.fill(TRUEGREEN)
                if self.oldsnake:
                    go_surf = self.score_font.render(oldtitle, True, BLACK);
                    go_rect = go_surf.get_rect()
                    GAME_SURFACE.blit(go_surf, ((GAME_W - go_rect.width) // 2, (GAME_H - go_rect.height) // 2))
                else:
                    GAME_SURFACE.blit(titleimage, ((GAME_W - titleimage.get_width()) // 2, (GAME_H - titleimage.get_height()) // 2))
                
                    # scrolltext
                    self.scroll_rect.x -= SCROLLTEXT_SPEED
                    if self.scroll_rect.right <= 0:           # if scrolled to end
                        self.scroll_rect.x = GAME_W*2         # then move to right side
                    GAME_SURFACE.blit(self.scroll_text, self.scroll_rect)
            else:
                # lcd ghosting effect. get game surface
                self.ghost_layer.blit(GAME_SURFACE, (0, 0))

                # fade-out using temporary surface
                ghost_cover = pygame.Surface((GAME_W, GAME_H))
                ghost_cover.fill(GREEN)
                ghost_cover.set_alpha(128)

                self.ghost_layer.blit(ghost_cover, (0, 0))

                # emoty game surface
                GAME_SURFACE.fill(TRUEGREEN)

                # add ghost layer on top
                GAME_SURFACE.blit(self.ghost_layer, (0, 0))
                    
                # then the rest of the drawing
                self.draw()
                if not self.oldsnake:
                    score_text = "{:04d}".format(self.score)
                    score_surface = self.score_font.render(score_text, True, BLACK)
                    GAME_SURFACE.blit(score_surface, (OFFSET - 4, OFFSET - 60 + 42))
                
                if self.status == 'GAME_OVER':
                    go_surf = self.scroll_font.render(self.gameover_text, True, BLACK);
                    if self.oldsnake:
                        temp_surface = pygame.Surface(go_surf.get_size())
                        temp_surface.fill(TRUEGREEN)
                        temp_surface.blit(go_surf, (0, 0))
                        go_surf.blit(temp_surface, (0, 0))
                    go_rect = go_surf.get_rect()
                    y = OFFSET - 60 + 42 + 5
                    if self.oldsnake:
                        y = (GAME_H - SCROLL_FONT_SIZE) // 2
                    GAME_SURFACE.blit(go_surf, ( (GAME_W-go_rect.right)//2, y))

                if self.active_timer:
                    total_seconds = 9 - (self.num_of_frames // FRAME_RATE)
                    if total_seconds < 1:
                        total_seconds = 0
                        self.reset_timer()
                    self.num_of_frames += 1
                if self.active_timer:
                    animal_rect = pygame.Rect(OFFSET - FONT_SIZE * 1.6 + CELL_SIZE * NUM_OF_CELLS_WIDTH - CELL_SIZE/2, OFFSET - 60 + TOP_OFFSET + FONT_SIZE / 4 - CELL_SIZE/4, round(CELL_SIZE*1.5), round(CELL_SIZE*1.5))
                    GAME_SURFACE.blit(self.animal.bigimage, animal_rect)
                    seconds_surface = self.score_font.render(str(total_seconds % 60), True, BLACK)
                    GAME_SURFACE.blit(seconds_surface, (OFFSET - FONT_SIZE / 1.7 + CELL_SIZE * NUM_OF_CELLS_WIDTH, OFFSET - 60 + 42))

            WIN_W, WIN_H = MAIN_SCREEN.get_size()
            
            # game surface to middle of the screen
            MAIN_SCREEN.blit(GAME_SURFACE, (OFFSET_X - (1920-WIN_W)//2, OFFSET_Y - (1080-WIN_H)//2))
            
            # overlay
            if overlay:
                MAIN_SCREEN.blit(overlay, (-(1920-WIN_W)//2, -(1080-WIN_H)//2))

            # update display
            pygame.display.flip()
            #pygame.display.update()
            
            self.clock.tick(FRAME_RATE)


if __name__ == '__main__':
    try:
        while True:
            reinit_globals()
            game = Game(oldsnake)
            game.run()
            reinit_next_game()
    except KeyboardInterrupt:
        game.QUIT()
    
