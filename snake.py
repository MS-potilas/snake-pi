# Snake
# Created by Sara Martínez

import pygame, sys, random
from pygame.math import Vector2
from pygame.transform import flip, rotate, scale

SNAKE_UPDATE_MS = 166
FRAME_RATE = 30  # more authentic than 60 fps

CELL_SIZE = 20

NUM_OF_CELLS_WIDTH = 25
NUM_OF_CELLS_HEIGHT = 20
OFFSET = 56
leveys = 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_WIDTH
korkeus = 2 * OFFSET + CELL_SIZE * NUM_OF_CELLS_HEIGHT



# Colors (R, G, B)
GREEN = (112, 142, 83)
TRUEGREEN = (0x6d, 0x8b, 0x50)      # ghosting-efektin jälkeen jäävä vihreä
BLACK = (0x1f, 0x22, 0x18)


# alustetaan Pygame
pygame.init()

# haetaan näytön todellinen maksimiresoluutio (esim. 1920x1080 tai 1280x720)
display_info = pygame.display.Info()
SCREEN_W = display_info.current_w
SCREEN_H = display_info.current_h

# alkuperäisen Snake-pelin koko, laskettu yllä
GAME_W = leveys
GAME_H = korkeus

# lasketaan offset (siirtymä), eli kuinka paljon tyhjää jää reunoille
OFFSET_X = (SCREEN_W - GAME_W) // 2 + 3     # pientä viilausta oikealle
OFFSET_Y = (SCREEN_H - GAME_H) // 2 + 6     # ...ja vähän alaspäin


# luodaan KOKO NÄYTÖN kokoinen pinta
MAIN_SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)

try:
    # öadataan overlay-kuva (esim. nokia_case.png)
    # convert_alpha() tekee kuvasta nopeamman piirtää ja säilyttää läpinäkyvyyden
    overlay = pygame.image.load("images/nokia_case.png").convert_alpha()
    
except:
    print("Overlay-kuvaa ei löytynyt, jatketaan ilman kuoria.")

titleimage = pygame.image.load("images/snake_pi.png")


# luodaan erillinen "virtuaalinen" pinta itse pelille
GAME_SURFACE = pygame.Surface((GAME_W, GAME_H))

pygame.mouse.set_visible(False) # Hide cursor here
score_font = pygame.font.Font("fonts/VT323-Regular.ttf", 50)


IMG_NAMES = ["food", "head", "body", "tail", "turn", "animal1", "animal2", "animal3", "animal4", "animal5", "animal6"]
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
    "animal1": scale(IMAGES["animal1"], (CELL_SIZE, CELL_SIZE)),
    "animal2": scale(IMAGES["animal2"], (CELL_SIZE, CELL_SIZE)),
    "animal3": scale(IMAGES["animal3"], (CELL_SIZE, CELL_SIZE)),
    "animal4": scale(IMAGES["animal4"], (CELL_SIZE, CELL_SIZE)),
    "animal5": scale(IMAGES["animal5"], (CELL_SIZE, CELL_SIZE)),
    "animal6": scale(IMAGES["animal6"], (CELL_SIZE, CELL_SIZE))
}

# User events
SNAKE_UPDATE = pygame.USEREVENT + 1

pygame.time.set_timer(SNAKE_UPDATE, SNAKE_UPDATE_MS)

pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()


# hätäisesti tehty joystickejä lukeva luokka
class Joystick:
    def __init__(self):
        self.x_move = 0
        self.y_move = 0
        self.buttons = []
        pygame.joystick.init()
        self.numsticks = pygame.joystick.get_count()
        self.sticknames = []
        for i in range(self.numsticks):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            name = joystick.get_name()
            self.sticknames.append(name)
        
    def get_joy(self):
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
        self.x_move = 0
        self.y_move = 0
        self.buttons = []
        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            axes = joystick.get_numaxes()
            for ii in range(axes):
                axis = joystick.get_axis(ii)
                if ii == 0:
                    if axis < -0.5:
                        self.x_move = -1
                    if axis > 0.5:
                        self.x_move = 1
                if ii == 1:
                    if axis < -0.5:
                        self.y_move = -1
                    if axis > 0.5:
                        self.y_move = 1
            numbuttons = joystick.get_numbuttons()
            for i in range(numbuttons):
                buttonval = joystick.get_button(i)
                if buttonval and not i in self.buttons:
                    self.buttons.append(i)


class Snake:
    def __init__(self):
        self.body = [Vector2(5, 12), Vector2(4, 12), Vector2(3, 12)]
        self.body_directions = ["R", "R", "R"]
        self.direction = Vector2(1, 0)
        self.last_direction = self.direction
        self.add_block = False
        self.eat_sound = pygame.mixer.Sound("sounds/eat.wav")
        self.wall_hit_sound = pygame.mixer.Sound("sounds/game_over.wav")

    def get_direction_name(self):
        if self.direction == Vector2(-1, 0):
            return "L"
        elif self.direction == Vector2(0, -1):
            return "U"
        elif self.direction == Vector2(0, 1):
            return "D"
        else:
            return "R"

    def get_block_image(self, index):
        if index == 0:
            return FORMAT_IMAGES["head_" + self.get_direction_name()]
        else:
            direction = self.body_directions[index]
            prev_direction = self.body_directions[index - 1]
            if index == len(self.body) - 1:
                return FORMAT_IMAGES["tail_" + prev_direction]
            elif direction != prev_direction:
                if (prev_direction == "R" and direction == "D") or (prev_direction == "U" and direction == "L"):
                    return FORMAT_IMAGES["turn_U"]
                elif (prev_direction == "L" and direction == "U") or (prev_direction == "D" and direction == "R"):
                    return FORMAT_IMAGES["turn_L"]
                elif (prev_direction == "R" and direction == "U") or (prev_direction == "D" and direction == "L"):
                    return FORMAT_IMAGES["turn_R"]
                else:
                    return FORMAT_IMAGES["turn_D"]
            else:
                return FORMAT_IMAGES["body_" + prev_direction]
    
    def draw(self):
        for index, block in enumerate(self.body):
            snake_surface = self.get_block_image(index)
            block_rect = pygame.Rect(OFFSET + block.x * CELL_SIZE, OFFSET + block.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            GAME_SURFACE.blit(snake_surface, block_rect)

    def update(self):
        self.body.insert(0, self.body[0] + self.direction)
        self.body_directions.insert(0, self.get_direction_name())
        if self.add_block == True:
            self.add_block = False
        else:
            self.body = self.body[:-1]
            self.body_directions = self.body_directions[:-1]
        self.last_direction = self.direction

    def reset(self):
        self.body = [Vector2(5, 12), Vector2(4, 12), Vector2(3, 12)]
        self.body_directions = ["R", "R", "R"]
        self.direction = Vector2(1, 0)
        self.last_direction = self.direction


class Food:
    def __init__(self, snake_body):
        self.position = self.create_random_pos(snake_body)

    def draw(self):
        food_surface = FORMAT_IMAGES["food"]
        food_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE, OFFSET + self.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        GAME_SURFACE.blit(food_surface, food_rect)

    def create_random_cell(self):
        x = random.randint(0, NUM_OF_CELLS_WIDTH - 1)
        y = random.randint(0, NUM_OF_CELLS_HEIGHT - 1)
        return Vector2(x, y)

    def create_random_pos(self, snake_body):
        position = self.create_random_cell()
        while position in snake_body:
            position = self.create_random_cell()
        return position


class Animal:
    def __init__(self, snake_body, food_position, active_timer):
        self.position = self.create_random_pos(snake_body, food_position)
        self.image = FORMAT_IMAGES["animal1"]
    
    def create_random_image(self):
        random_number = random.randint(1, 6)
        random_animal_surface = FORMAT_IMAGES["animal" + str(random_number)]
        return random_animal_surface
    
    def draw(self, active_timer):
        if active_timer:
            animal_surface = self.image
            animal_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE, OFFSET + self.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            GAME_SURFACE.blit(animal_surface, animal_rect)
    
    def create_random_cell(self):
        x = random.randint(0, NUM_OF_CELLS_WIDTH - 1)
        y = random.randint(0, NUM_OF_CELLS_HEIGHT - 1)
        return Vector2(x, y)

    def create_random_pos(self, snake_body, food_position):
        position = self.create_random_cell()
        while position in snake_body or position == food_position:
            position = self.create_random_cell()
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
        self.ui_timer = False
        self.animal = Animal(self.snake.body, self.food.position, self.active_timer)
        self.joysticks = Joystick()
        self.nokia_tune = pygame.mixer.Sound("sounds/nokia_tune.wav")
        
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

    def update_food_counter(self):
        if not self.active_timer:
            self.food_counter += 1
            if self.food_counter >= 5:
                # new random position, because snake and food have moved
                self.animal.position = self.animal.create_random_pos(self.snake.body, self.food.position)
                self.active_timer = True

    def check_collision_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.snake.eat_sound.play()
            self.food.position = self.food.create_random_pos(self.snake.body)
            self.snake.add_block = True
            self.score += 7
            self.update_food_counter()

    def reset_timer(self):
        self.food_counter = 0
        self.num_of_frames = 0
        self.active_timer = False
        self.ui_timer = False
        self.animal.image = self.animal.create_random_image()

    def check_collision_with_animal(self):
        if self.snake.body[0] == self.animal.position and self.active_timer:
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
        self.snake.wall_hit_sound.play()
        self.status = "GAME_OVER"
        self.reset_timer()
        self.ui_timer = True

    def QUIT(self):
        pygame.quit()
        sys.exit()
        


    def run(self):
        self.nokia_tune.play()
        while True:                
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.QUIT()
                if ev.type == pygame.KEYDOWN:
                    # ESCAPE or Q key quits
                    if ev.key == pygame.K_ESCAPE or ev.key == pygame.K_q:
                        self.QUIT()
                if ev.type == SNAKE_UPDATE:
                    self.joysticks.get_joy()
                    if self.status == 'PLAYING':
                        if self.joysticks.y_move == -1 and self.snake.last_direction != Vector2(0, 1):
                            self.snake.direction = Vector2(0, -1)
                        elif self.joysticks.y_move == 1 and self.snake.last_direction != Vector2(0, -1):
                            self.snake.direction = Vector2(0, 1)
                        elif self.joysticks.x_move == -1 and self.snake.last_direction != Vector2(1, 0):
                            self.snake.direction = Vector2(-1, 0)
                        elif self.joysticks.x_move == 1 and self.snake.last_direction != Vector2(-1, 0):
                            self.snake.direction = Vector2(1, 0)
                    if len(self.joysticks.buttons):
                        # upper buttons:
                        for j in range(6,15):
                            if j in self.joysticks.buttons:
                                self.QUIT()
                    if (self.status == "PRE_GAME" or (self.status == "GAME_OVER" and total_seconds < 8)) and (len(self.joysticks.buttons) or self.joysticks.y_move or self.joysticks.x_move):
                        self.snake.reset()
                        self.food.position = self.food.create_random_pos(self.snake.body)
                        self.score = 0
                        self.status = "PLAYING"
                    self.update()
                if ev.type == pygame.KEYDOWN:
                    total_seconds = 9 - (self.num_of_frames // FRAME_RATE)
                    if self.status == "PRE_GAME" or (self.status == "GAME_OVER" and total_seconds < 8):
                        self.snake.reset()
                        self.food.position = self.food.create_random_pos(self.snake.body)
                        self.score = 0
                        self.status = "PLAYING"
                    if self.status == 'PLAYING':
                        if ev.key == pygame.K_UP and self.snake.last_direction != Vector2(0, 1):
                            self.snake.direction = Vector2(0, -1)
                        if ev.key == pygame.K_DOWN and self.snake.last_direction != Vector2(0, -1):
                            self.snake.direction = Vector2(0, 1)
                        if ev.key == pygame.K_LEFT and self.snake.last_direction != Vector2(1, 0):
                            self.snake.direction = Vector2(-1, 0)
                        if ev.key == pygame.K_RIGHT and self.snake.last_direction != Vector2(-1, 0):
                            self.snake.direction = Vector2(1, 0)
                        

            if self.status == 'PRE_GAME':
                # title screen
                GAME_SURFACE.fill(TRUEGREEN)
                GAME_SURFACE.blit(titleimage, (68, 68))
            else:
                # luodaan väliaikainen pinta haamuefektiä varten (saman kokoinen kuin GAME_SURFACE)
                ghost_cover = pygame.Surface((GAME_W, GAME_H))
                # täytetään se vihreällä
                ghost_cover.fill(GREEN) 
                # määritetään läpinäkyvyys (Alpha: 0 = täysin näkymätön, 255 = täysin peittävä)
                ghost_cover.set_alpha(176)    # alle 100 jätti haamukuvaa pi:llä (pygame versio < 2)

                # liiteätän osin läpinäkyvä pinta pelialueen päälle
                # ei pyyhi vanhaa näyttöä kokonaan, vaan jättää sen haalistumaan taustalle
                GAME_SURFACE.blit(ghost_cover, (0, 0))
            
                pygame.draw.rect(GAME_SURFACE, BLACK, (OFFSET - 4, OFFSET - 4, CELL_SIZE * NUM_OF_CELLS_WIDTH + 8, CELL_SIZE * NUM_OF_CELLS_HEIGHT + 8), 4)
                pygame.draw.line(GAME_SURFACE, BLACK, (OFFSET - 4, OFFSET - 12), (OFFSET + 4 + CELL_SIZE * NUM_OF_CELLS_WIDTH, OFFSET - 12), 4)
                self.draw()
                score_surface = score_font.render(str(self.score), True, BLACK)
                GAME_SURFACE.blit(score_surface, (OFFSET - 4, -4))

                if self.active_timer or self.ui_timer:
                    total_seconds = 9 - (self.num_of_frames // FRAME_RATE)
                    if total_seconds < 1:
                        total_seconds = 0
                        if self.ui_timer and self.status == 'GAME_OVER':
                            self.status = "PRE_GAME"
                        self.reset_timer()
                    self.num_of_frames += 1
                if self.active_timer:
                    animal_rect = pygame.Rect(OFFSET - 48 + CELL_SIZE * NUM_OF_CELLS_WIDTH, 16, CELL_SIZE, CELL_SIZE)
                    GAME_SURFACE.blit(self.animal.image, animal_rect)
                    seconds_surface = score_font.render(str(total_seconds % 60), True, BLACK)
                    GAME_SURFACE.blit(seconds_surface, (OFFSET - 12 + CELL_SIZE * NUM_OF_CELLS_WIDTH, -2))

            # pelialue päänäytön keskelle laskettuihin koordinaatteihin
            MAIN_SCREEN.blit(GAME_SURFACE, (OFFSET_X, OFFSET_Y))
            
            # PÄÄLLE OVERLAY
            MAIN_SCREEN.blit(overlay, (0, 0))

            # Päivitetään näyttö
            pygame.display.flip()

            #pygame.display.update()
            self.clock.tick(FRAME_RATE)


if __name__ == '__main__':
    try:
        pygame.display.set_caption("Snake")
        game = Game()
        game.run()
    except KeyboardInterrupt:
        game.QUIT()
    
