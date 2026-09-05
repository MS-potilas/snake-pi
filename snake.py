#!/usr/bin/python3
import pygame, sys, random, glob, os, shelve
from pygame.math import Vector2
from pygame.transform import flip, rotate, scale


# original Snake created by Sara Martínez
#
# Snake Pi modifications by MS-potilas 2026
# Snake Pi made for RetroPie, but can be run also without it.


FRAME_RATE = 30         # more authentic than 60 fps

SNAKE_UPDATE_MS = 180
ENABLE_INPUT_AFTER_GAMEOVER_MS = 3000
GAMEOVER_TIMEOUT_MS = 10000
PLAY_TITLE_MUSIC_AFTER_MS = 420

# Colors (R, G, B)
GREEN = (112, 142, 83)
TRUEGREEN = (0x6d, 0x8b, 0x50)      # green left after ghosting effect
BLACK = (0x1f, 0x22, 0x18)          # greenish LCD-black
LESSBLACK = (0x30, 0x35, 0x2A)      # something odd

ANIMAL_FREQUENCY = 5        # normal is 5

FONT_SIZE = 34
SCROLL_FONT_SIZE = 24
TOP_OFFSET = 40
OFFSET = 80

CELL_SIZE = 22    # 20 is compatible with the overlay
NUM_OF_CELLS_WIDTH = 29
NUM_OF_CELLS_HEIGHT = 19

cmdline = " " + (" ".join(sys.argv)) + " "

if " --7110" in cmdline:
    casename = 'images/nokia_case7110.png'
elif " --3310" in cmdline:
    casename = 'images/nokia_case3310.png'
elif " --nocase" in cmdline:
    casename = ''
else:
    casename = random.choice(glob.glob('images/nokia_case*.png'))

if '7110' in casename:
    # same area as with 3310 works, but this is more optimized:
    NUM_OF_CELLS_WIDTH = 26
    NUM_OF_CELLS_HEIGHT = 21


# game area size
GAME_W = 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_WIDTH
GAME_H = TOP_OFFSET + 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_HEIGHT

# scroll text

scrolltext = "      Welcome to Snake Pi, a remake of the 1998 Nokia game Snake II. Snake Pi was made specifically for RetroPie. Thanks to Sara Martinez for the groundwork. Best regards, MS-potilas 2026.    Feel free to copy and reuse my work.    High score is [HS]."

SCROLLTEXT_SPEED = 4


# alustetaan Pygame
pygame.init()

# get full screen size (for example 1920x1080 or 1280x720)
display_info = pygame.display.Info()
FULL_SCREEN_W = display_info.current_w
FULL_SCREEN_H = display_info.current_h

# overlay image size
OVERLAY_W = 1920
OVERLAY_H = 1080

# calculate game area offset
OFFSET_X = (OVERLAY_W - GAME_W) // 2
OFFSET_Y = (OVERLAY_H - GAME_H) // 2


def is_windowing_system():
    if sys.platform == 'windows' or sys.platform == 'darwin': # windows or mac
        return True
    if os.environ.get('DISPLAY'):
        return True
    return False


fullscreen = False

if (is_windowing_system() and not " --fullscreen " in cmdline) or " --windowed " in cmdline:
    # create a window (under X or Wayland, for example)
    MAIN_SCREEN = pygame.display.set_mode((1280, 720), pygame.RESIZABLE )
    pygame.display.set_caption("Snake Pi")
else:
    # create full screen display 
    MAIN_SCREEN = pygame.display.set_mode((FULL_SCREEN_W, FULL_SCREEN_H), pygame.FULLSCREEN | pygame.NOFRAME )
    pygame.mouse.set_visible(False)         # hide mouse cursor
    fullscreen = True



pygame.key.set_repeat(50, SNAKE_UPDATE_MS)

# change working dir to same as the script's
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

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


IMG_NAMES = ["food", "head", "body", "tail", "turn", "fhead", "fbody", "ftail", "fturn", "animal1", "animal2", "animal3", "animal4", "animal5", "animal6"]
IMAGES = { name: pygame.image.load("images/" + "{}.png".format(name)) for name in IMG_NAMES}
FORMAT_IMAGES = {
    "food": scale(IMAGES["food"], (CELL_SIZE, CELL_SIZE)),
    "head_R": scale(IMAGES["head"], (CELL_SIZE, CELL_SIZE)),
    "head_L": flip(scale(IMAGES["head"], (CELL_SIZE, CELL_SIZE)), True, False),
    "head_U": rotate(scale(IMAGES["head"], (CELL_SIZE, CELL_SIZE)), 90),
    "head_D": flip(rotate(scale(IMAGES["head"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "body_R": scale(IMAGES["body"], (CELL_SIZE, CELL_SIZE)),
    "body_L": flip(scale(IMAGES["body"], (CELL_SIZE, CELL_SIZE)), True, False),
    "body_U": rotate(scale(IMAGES["body"], (CELL_SIZE, CELL_SIZE)), 90),
    "body_D": flip(rotate(scale(IMAGES["body"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "tail_R": scale(IMAGES["tail"], (CELL_SIZE, CELL_SIZE)),
    "tail_L": flip(scale(IMAGES["tail"], (CELL_SIZE, CELL_SIZE)), True, False),
    "tail_U": rotate(scale(IMAGES["tail"], (CELL_SIZE, CELL_SIZE)), 90),
    "tail_D": flip(rotate(scale(IMAGES["tail"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "turn_R": scale(IMAGES["turn"], (CELL_SIZE, CELL_SIZE)),
    "turn_L": flip(scale(IMAGES["turn"], (CELL_SIZE, CELL_SIZE)), True, False),
    "turn_U": rotate(scale(IMAGES["turn"], (CELL_SIZE, CELL_SIZE)), 90),
    "turn_D": rotate(scale(IMAGES["turn"], (CELL_SIZE, CELL_SIZE)), 180),
    "fhead_R": scale(IMAGES["fhead"], (CELL_SIZE, CELL_SIZE)),
    "fhead_L": flip(scale(IMAGES["fhead"], (CELL_SIZE, CELL_SIZE)), True, False),
    "fhead_U": rotate(scale(IMAGES["fhead"], (CELL_SIZE, CELL_SIZE)), 90),
    "fhead_D": flip(rotate(scale(IMAGES["fhead"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "fbody_R": scale(IMAGES["fbody"], (CELL_SIZE, CELL_SIZE)),
    "fbody_L": flip(scale(IMAGES["fbody"], (CELL_SIZE, CELL_SIZE)), True, False),
    "fbody_U": rotate(scale(IMAGES["fbody"], (CELL_SIZE, CELL_SIZE)), 90),
    "fbody_D": flip(rotate(scale(IMAGES["fbody"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "ftail_R": scale(IMAGES["ftail"], (CELL_SIZE, CELL_SIZE)),
    "ftail_L": flip(scale(IMAGES["ftail"], (CELL_SIZE, CELL_SIZE)), True, False),
    "ftail_U": rotate(scale(IMAGES["ftail"], (CELL_SIZE, CELL_SIZE)), 90),
    "ftail_D": flip(rotate(scale(IMAGES["ftail"], (CELL_SIZE, CELL_SIZE)), 270), True, False),
    "fturn_R": scale(IMAGES["fturn"], (CELL_SIZE, CELL_SIZE)),
    "fturn_L": flip(scale(IMAGES["fturn"], (CELL_SIZE, CELL_SIZE)), True, False),
    "fturn_U": rotate(scale(IMAGES["fturn"], (CELL_SIZE, CELL_SIZE)), 90),
    "fturn_D": rotate(scale(IMAGES["fturn"], (CELL_SIZE, CELL_SIZE)), 180),
    "animal1": scale(IMAGES["animal1"], (CELL_SIZE, CELL_SIZE)),
    "animal2": scale(IMAGES["animal2"], (CELL_SIZE, CELL_SIZE)),
    "animal3": scale(IMAGES["animal3"], (CELL_SIZE, CELL_SIZE)),
    "animal4": scale(IMAGES["animal4"], (CELL_SIZE, CELL_SIZE)),
    "animal5": scale(IMAGES["animal5"], (CELL_SIZE, CELL_SIZE)),
    "animal6": scale(IMAGES["animal6"], (CELL_SIZE, CELL_SIZE))
}

# User events
EV_SNAKE_UPDATE = pygame.USEREVENT + 1
EV_ENABLE_INPUT = pygame.USEREVENT + 2
EV_GAME_OVER_TIMEOUT = pygame.USEREVENT + 3
EV_PLAY_MUSIC = pygame.USEREVENT + 4

pygame.time.set_timer(EV_SNAKE_UPDATE, SNAKE_UPDATE_MS)
pygame.time.set_timer(EV_PLAY_MUSIC, PLAY_TITLE_MUSIC_AFTER_MS)
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


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
    def __init__(self):
        self.body = []
        self.body_directions = []
        self.body_foods = []
        self.direction = Vector2(-1, -1)
        self.current_direction = self.direction
        self.reset()
        self.add_block = False
        self.eat_sound = pygame.mixer.Sound("sounds/eat.wav")
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
        self.body = [Vector2(5, 12), Vector2(4, 12), Vector2(3, 12)]
        self.body_directions = ["R", "R", "R"]
        self.body_foods = [0, 0, 0]
        self.direction = Vector2(1, 0)
        self.current_direction = self.direction


class Food:
    def __init__(self, snake_body):
        self.position = self.create_random_pos(snake_body)

    def draw(self):
        food_surface = FORMAT_IMAGES["food"]
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
        self.image = FORMAT_IMAGES["animal1"]
        self.bigimage =  scale(self.image, (round(CELL_SIZE*1.5), round(CELL_SIZE*1.5)))

    
    def create_random_image(self):
        random_number = random.randint(1, 6)
        random_animal_surface = FORMAT_IMAGES["animal" + str(random_number)]
        return random_animal_surface
    
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
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food(self.snake.body)
        #self.status = "PLAYING"
        self.status = "PRE_GAME"
        self.score = 0
        self.food_counter = 0
        self.num_of_frames = 0
        self.active_timer = False
        self.animal = Animal(self.snake.body, self.food.position, self.active_timer)
        self.joysticks = Joystick()
        # select random nokia tune for title screen
        tunename = random.choice(glob.glob('sounds/nokia_tune*.wav'))
        self.nokia_tune = pygame.mixer.Sound(tunename)
        self.score_font = pygame.font.Font("fonts/nokiafc22.ttf", FONT_SIZE)
        self.input_active = True

        self.scroll_font = pygame.font.Font("fonts/nokiafc22.ttf", SCROLL_FONT_SIZE)
        
        self.high_score = 0
        self.load_highscore()
        self.scroll_text = None
        self.scroll_rect = None
        self.update_scrolltext()
    
    def load_highscore(self):
        try:
            d = shelve.open('.highscore')
            self.high_score = d['highscore']
            d.close()
        except:
            pass
            
    def save_highscore(self):
        d = shelve.open('.highscore')
        d['highscore'] = self.high_score
        d.close()        
    
    def update_scrolltext(self):
        scrolltext_hs = scrolltext.replace('[HS]', str(self.high_score))
        self.scroll_text = self.scroll_font.render(scrolltext_hs, True, LESSBLACK)
        self.scroll_rect = self.scroll_text.get_rect(left=GAME_W, top=GAME_H - OFFSET - round(FONT_SIZE))
        
        
    def draw(self):
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
            if self.food_counter >= ANIMAL_FREQUENCY: 
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

    def reset_timer(self):
        self.food_counter = 0
        self.num_of_frames = 0
        self.active_timer = False
        self.animal.image = self.animal.create_random_image()
        self.animal.bigimage =  scale(self.animal.image, (round(CELL_SIZE*1.5), round(CELL_SIZE*1.5)))

    def check_collision_with_animal(self):
        if self.snake.body[0] == self.animal.position and self.active_timer:
            self.snake.body_foods[0] = 1
            self.snake.eat_sound.play()
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
        
        if self.score > self.high_score:
            self.snake.highscore_sound.play()
            self.high_score = self.score
            self.save_highscore()
        else:
            self.snake.gameover_sound.play()
            
        self.status = "GAME_OVER"
        pygame.time.set_timer(EV_GAME_OVER_TIMEOUT, GAMEOVER_TIMEOUT_MS)
        pygame.time.set_timer(EV_ENABLE_INPUT, ENABLE_INPUT_AFTER_GAMEOVER_MS)
        self.input_active = False

    def play(self):
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
                GAME_SURFACE.blit(titleimage, (GAME_W/2 - titleimage.get_width()/2, GAME_H/2 - titleimage.get_height()/2))
                
                # scrolltext
                self.scroll_rect.x -= SCROLLTEXT_SPEED
                if self.scroll_rect.right <= 0:           # if scrolled to end
                    self.scroll_rect.x = GAME_W*2         # then move to right side
                GAME_SURFACE.blit(self.scroll_text, self.scroll_rect)
                
            else:
                # temporary surface for lcd ghosting effect
                ghost_cover = pygame.Surface((GAME_W, GAME_H))
                ghost_cover.fill(GREEN) 
                # opacity (Alpha: 0 = fully transparent, 255 = opaque)
                ghost_cover.set_alpha(176)    # under 100 left permanent ghost marks

                # put semi-transparent surface onto game surface
                # old surface omage is left under it to fade away slowly
                GAME_SURFACE.blit(ghost_cover, (0, 0))
            
                pygame.draw.rect(GAME_SURFACE, BLACK, (OFFSET - 4, TOP_OFFSET + OFFSET - 4, CELL_SIZE * NUM_OF_CELLS_WIDTH + 8, CELL_SIZE * NUM_OF_CELLS_HEIGHT + 8), 5)
                pygame.draw.line(GAME_SURFACE, BLACK, (OFFSET - 4, TOP_OFFSET + OFFSET - 14), (OFFSET + 4 + CELL_SIZE * NUM_OF_CELLS_WIDTH, TOP_OFFSET + OFFSET - 14), 5)
                self.draw()
                score_surface = self.score_font.render("{:04d}".format(self.score), True, BLACK)
                GAME_SURFACE.blit(score_surface, (OFFSET - 4, OFFSET - 60 + 42))

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
            MAIN_SCREEN.blit(GAME_SURFACE, (OFFSET_X - (1920-WIN_W)/2, OFFSET_Y - (1080-WIN_H)/2))
            
            # overlay
            if overlay:
                MAIN_SCREEN.blit(overlay, (-(1920-WIN_W)/2, -(1080-WIN_H)/2))



            # update display
            pygame.display.flip()
            #pygame.display.update()
            
            self.clock.tick(FRAME_RATE)


if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        game.QUIT()
    
