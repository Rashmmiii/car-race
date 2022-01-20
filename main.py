import pygame
import time
import math
from helper import scale_image  , blit_rotate_center , blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"),0.9)

TRACK_BORDER= scale_image(pygame.image.load("imgs/track-border.png"),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (130,250)

RED_CAR= scale_image(pygame.image.load("imgs/red-car.png"),0.5)
GREEN_CAR= scale_image(pygame.image.load("imgs/green-car.png"),0.5)

WIDTH,HEIGHT=TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("CAR-RACE")

MAIN_FONT = pygame.font.SysFont("comicsans",44)

class AbstractCar:
    
    def __init__(self,max_vel,rot_vel):
        self.max_vel=max_vel
        self.rot_vel=rot_vel
        self.vel=0
        self.angle=0
        self.img=self.IMG
        self.x , self.y = self.START_POS
        self.acc = 0.1
    
    def rotate(self, left=False , right=False):
        if left:
            self.angle+=self.rot_vel
        elif right:
            self.angle-=self.rot_vel

    def draw(self,win):
        blit_rotate_center(win , self.img , (self.x ,self.y) ,self.angle)

    def move_forward(self):
        self.vel=min(self.vel+self.acc,self.max_vel)
        self.move()

    def move_backward(self):
        self.vel=min(self.vel-self.acc, -self.max_vel/2)
        self.move()
    
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians)*self.vel
        horizontal = math.sin(radians)*self.vel

        self.x-=horizontal
        self.y-=vertical

    def collide(self,mask,x=0,y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x,self.y = self.START_POS
        self.vel=0
        self.angle=0
        

class PlayerCar(AbstractCar):
    IMG=RED_CAR
    START_POS = (180,200)
    def reduce_speed(self):
        self.vel=max(self.vel - self.acc/1.7 ,0 )
        self.move()

    def bounce(self):
        self.vel= -self.vel/1.5
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150,200)

    def __init__(self, max_vel, rot_vel, path=[]):
        super().__init__(max_vel, rot_vel)
        self.path=path
        self.current_point=0
        self.vel=max_vel

    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win , (255,0,0), point ,5)

    def draw(self,win):
        super().draw(win)
        #self.draw_points(win)

    def calculate_angle(self):
        target_x,target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_rad_angle= math.pi/2
        else:
            desired_rad_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_rad_angle+=math.pi

        diff_in_angle = self.angle -math.degrees(desired_rad_angle)
        if diff_in_angle >=180:
            diff_in_angle-=360

        if diff_in_angle>0:
            self.angle -= min(self.rot_vel,abs(diff_in_angle))
        else:
            self.angle += min(self.rot_vel,abs(diff_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x , self.y , self.img.get_width(), self.img.get_height() )
        if rect.collidepoint(*target):
            self.current_point+=1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self ,level):
        self.reset()
        self.vel=self.max_vel + (level-1)*0.2
        self.current_point=0

FPS=60
PATH = [ (179, 127), (104, 71), (52, 142), (64, 471), (334, 737), (407, 660), (416, 523), (517, 471), (603, 565), (623, 719), (742, 706), (731, 393), (439, 364), (427, 259), (719, 251), (732, 
100), (506, 68), (282, 95), (278, 383), (178, 396), (169, 261) ]
clock=pygame.time.Clock()

images = [(GRASS ,(0,0)) , (TRACK ,(0,0)) , (FINISH,FINISH_POS) , (TRACK_BORDER , (0,0) )]
player_car = PlayerCar(5,5)
computer_car = ComputerCar(2,3 ,PATH )

class GameInfo:
    LEVELS=10
    def __init__(self,level=1):
        self.level=level
        self.started=False
        self.level_start_time=0

    def next_level(self):
        self.level+=1
        self.started=False

    def reset(self):
        self.level=1
        self.started=False
        self.level_start_time=0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started=True
        self.level_start_time= time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round( time.time() - self.level_start_time)


def draw(win,images,player_car ,computer_car, game_info):
    for img,pos in images:
        win.blit(img,pos)

    level_text = MAIN_FONT.render(f"level : {game_info.level}" , 1, (255,255,255))
    win.blit(level_text , (10, HEIGHT - level_text.get_height() - 73))

    time_text = MAIN_FONT.render(f"Time : {game_info.get_level_time()}s" , 1, (255,255,255))
    win.blit(time_text , (10, HEIGHT - time_text.get_height() - 35))

    playervel_text = MAIN_FONT.render(f"Vel : {round(player_car.vel,1)}px/s" , 1, (255,255,255))
    win.blit(playervel_text , (10, HEIGHT - playervel_text.get_height() - 7))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved=False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved=True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved=True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car , computer_car , game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_col = computer_car.collide(FINISH_MASK , *FINISH_POS)
    if computer_finish_poi_col!=None:
        blit_text_center(WIN,MAIN_FONT , "Oh, Better luck next time!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    player_finish_poi_col = player_car.collide(FINISH_MASK , *FINISH_POS)
    if player_finish_poi_col != None:
        if(player_finish_poi_col[1]==0):
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)

game_info = GameInfo()

run = True
while run:
    clock.tick(FPS)

    draw(WIN,images,player_car ,computer_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT , f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
            break

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     pos=pygame.mouse.get_pos()
        #     computer_car.path.append(pos)

    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car , game_info)

    if game_info.game_finished():
        blit_text_center(WIN,MAIN_FONT , "Yay You Won!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

# print(computer_car.path)
pygame.quit()      