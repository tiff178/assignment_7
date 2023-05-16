import numpy as np
import pygame as pg
from random import randint, gauss
import random

pg.init()
pg.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 220, 255)
BLUE = (153, 153, 255)
RED = (255, 0, 0)
PURPLE = (220, 200, 255)

SCREEN_SIZE = (800, 600)


def rand_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

class GameObject:

    def move(self):
        pass
    
    def draw(self, screen):
        pass  

class Shell(GameObject):
    '''
    The ball class. Creates a ball, controls it's movement and implement it's rendering.
    '''
    def __init__(self, coord, vel, rad=20, color=None):
        '''
        Constructor method. Initializes ball's parameters and initial values.
        '''
        self.coord = coord
        self.vel = vel
        if color == None:
            color = rand_color()
        self.color = color
        self.rad = rad
        self.is_alive = True

    def check_corners(self, refl_ort=0.8, refl_par=0.9):
        '''
        Reflects ball's velocity when ball bumps into the screen corners. Implemetns inelastic rebounce.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)

    def move(self, time=1, grav=0):
        '''
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        '''
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def draw(self, screen):
        '''
        Draws the ball on appropriate surface.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)


class Cannon(GameObject):
    '''
    Cannon class. Manages it's renderring, movement and striking.
    '''
    def __init__(self, coord=[30, SCREEN_SIZE[1]-50], angle=0, max_pow=50, min_pow=10, color=PINK):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow
    
    def activate(self):
        '''
        Activates gun's charge.
        '''
        self.active = True

    def gain(self, inc=2):
        '''
        Increases current gun charge power.
        '''
        if self.active and self.pow < self.max_pow:
            self.pow += inc

    def strike(self):
        '''
        Creates ball, according to gun's direction and current charge power.
        '''
        vel = self.pow
        angle = self.angle
        ball = Shell(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        return ball
        
    def set_angle(self, target_pos):
        '''
        Sets gun's direction to target position.
        '''
        self.angle = np.arctan2(target_pos[1] - self.coord[1], target_pos[0] - self.coord[0])

    def move(self, inc_x):
        '''
        Changes horizontal position of the tank. 
        '''
        x = self.coord[0] + inc_x
        if x > SCREEN_SIZE[0] - 30:
            self.coord[0] = SCREEN_SIZE[0] - 30
        elif x < 30:
            self.coord[0] = 30
        else:
            self.coord[0] = x

    def draw(self, screen):
        '''
        Draws the tank with cannon (gun) on the screen.
        '''
        # Tank Shape
        static_rect = pg.Rect(self.coord[0] - 60//2, self.coord[1], 55, 15)
        pg.draw.rect(screen, self.color, static_rect)
        pg.draw.circle(screen, self.color,
                       (self.coord[0] - 16, self.coord[1] + 18), 7) # back wheel
        pg.draw.circle(screen, self.color,
                       (self.coord[0] + 13, self.coord[1] + 18), 7) # front wheel

        # shape of the cannon (gun)
        gun_shape = []
        vec_1 = np.array([int(5*np.cos(self.angle - np.pi/2)), int(5*np.sin(self.angle - np.pi/2))])
        vec_2 = np.array([int(self.pow*np.cos(self.angle)), int(self.pow*np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)

class Enemy(Cannon):
    '''
    Enemy class. Manages it's renderring, movement and striking. This is the rival cannon (enemy) that will attack current cannon.
    '''
    def __init__(self, coord=[200, SCREEN_SIZE[1]-50], angle=0, max_pow=50, min_pow=10, color=BLUE):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        super().__init__(coord, angle, max_pow, min_pow, color=BLUE)
        self.direction = 1
        self.move_counter = 0
        self.move_threshold = 50

    def move_left(self):
        self.move(-15)

    def move_right(self):
        self.move(15)

    def update(self):
        self.move_counter += 1
        if self.move_counter >= self.move_threshold:
            self.move_counter = 0
            self.direction *= -1
            if self.direction == -1:
                self.move_left()
            else:
                self.move_right()
        if random.randint(0,100) < 5:
            target_angle = random.uniform(-np.pi/4, np.pi/4)
            self.set_angle([self.coord[0] + 100 * np.cos(target_angle), self.coord[1] + 100 * np.sin(target_angle)])
            self.activate()
            return self.strike()

class Enemy2(Cannon):
    '''
    Enemy class. Manages it's renderring, movement and striking. This is the rival cannon (enemy) that will attack current cannon.
    '''
    def __init__(self, coord=[500, SCREEN_SIZE[1]-50], angle=0, max_pow=50, min_pow=10, color=WHITE):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        super().__init__(coord, angle, max_pow, min_pow, color=WHITE)
        self.direction = 1
        self.move_counter = 0
        self.move_threshold = 60

    def move_left(self):
        self.move(-20)

    def move_right(self):
        self.move(20)

    def update(self):
        self.move_counter += 1
        if self.move_counter >= self.move_threshold:
            self.move_counter = 0
            self.direction *= -1
            if self.direction == -1:
                self.move_left()
            else:
                self.move_right()
        if random.randint(0,100) < 5:
            target_angle = random.uniform(-np.pi/4, np.pi/4)
            self.set_angle([self.coord[0] + 100 * np.cos(target_angle), self.coord[1] + 100 * np.sin(target_angle)])
            self.activate()
            return self.strike()


class Target(GameObject):
    '''
    Target class. Creates target, manages it's rendering and collision with a ball event.
    '''
    def __init__(self, coord=None, color=None, rad=30):
        '''
        Constructor method. Sets coordinate, color and radius of the target.
        '''
        if coord == None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad

        if color == None:
            color = rand_color()
        self.color = color

    def check_collision(self, ball):
        '''
        Checks whether the ball bumps into target.
        '''
        dist = sum([(self.coord[i] - ball.coord[i])**2 for i in range(2)])**0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):
        '''
        Draws the target on the screen
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self):
        """
        This type of target can't move at all.
        :return: None
        """
        pass

# class MovingTargets(Target):
#     def __init__(self, coord=None, color=None, rad=30):
#         super().__init__(coord, color, rad)
#         self.vx = randint(-2, +2)
#         self.vy = randint(-2, +2)
    
#     def move(self):
#         self.coord[0] += self.vx
#         self.coord[1] += self.vy

class ButterflyTarget(Target):
    '''
    Butterfly class. Creates a butterfly target that moves horizontally back and forth across the screen.
    '''
    def __init__(self, coord=None, image=None, rad=30, speed=3):
        super().__init__(coord, image, rad)
        self.speed = speed
        self.direction = 1
        self.image = pg.image.load("butterfly.png")
        self.image = pg.transform.scale(self.image, (rad*2, rad*2))

    def move(self):
        self.coord[0] += self.direction * self.speed
        if self.coord[0] < self.rad or self.coord[0] > SCREEN_SIZE[0] - self.rad:
            self.direction *= -1
    
    def draw(self, screen):
        rect = self.image.get_rect()
        rect.center = self.coord
        screen.blit(self.image, rect)

class BirdTarget(Target):
    '''
    Bird class. Creates a bird target that moves diagonally across the screen.
    '''
    def __init__(self, coord=None, image=None, rad=30, speed=3):
        super().__init__(coord, image, rad)
        self.speed = speed
        self.x_direction = 1
        self.y_direction = 1
        self.image = pg.image.load("bird.png")
        self.image = pg.transform.scale(self.image, (rad*2, rad*2))

    def move(self):
        self.coord[0] += self.x_direction * self.speed
        self.coord[1] += self.y_direction * self.speed
        
        # Reverse direction when reaching the edges of the screen
        if self.coord[0] < self.rad or self.coord[0] > SCREEN_SIZE[0] - self.rad:
            self.x_direction *= -1
        if self.coord[1] < self.rad or self.coord[1] > SCREEN_SIZE[1] - self.rad:
            self.y_direction *= -1

    def draw(self, screen):
        rect = self.image.get_rect()
        rect.center = self.coord
        screen.blit(self.image, rect)

class ScoreTable:
    '''
    Score table class.
    '''
    def __init__(self, t_destr=0, b_used=0):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("dejavusansmono", 25)

    def score(self):
        '''
        Score calculation method.
        '''
        return self.t_destr - self.b_used

    def draw(self, screen):
        score_surf = []
        score_surf.append(self.font.render("Destroyed: {}".format(self.t_destr), True, BLACK))
        score_surf.append(self.font.render("Balls used: {}".format(self.b_used), True, BLACK))
        score_surf.append(self.font.render("Total: {}".format(self.score()), True, WHITE))
        for i in range(3):
            screen.blit(score_surf[i], [10, 10 + 30*i])

class Manager:
    '''
    Class that manages events' handling, ball's motion and collision, target creation, etc.
    '''
    def __init__(self, n_targets=1):
        self.balls = []
        self.gun = Cannon()
        self.targets = []
        self.score_t = ScoreTable()
        self.enemy = Enemy()
        self.enemy2 = Enemy2()
        self.n_targets = n_targets
        self.new_mission()

    def new_mission(self):
        '''
        Adds new targets.
        '''
        for i in range(self.n_targets):
            self.targets.append(BirdTarget(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            self.targets.append(Target(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            self.targets.append(ButterflyTarget(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
    
    def process(self, events, screen):
        '''
        Runs all necessary method for each iteration. Adds new targets, if previous are destroyed.
        '''
        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)
        
        self.move()
        self.collide()
        self.draw(screen)

        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_mission()

        return done

    def handle_events(self, events):
        '''
        Handles events from keyboard, mouse, etc.
        '''
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.gun.move(-10)
                elif event.key == pg.K_RIGHT:
                    self.gun.move(10)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
                    self.score_t.b_used += 1
        return done

    def draw(self, screen):
        '''
        Runs balls', gun's, targets' and score table's drawing method.
        '''
        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        self.gun.draw(screen)
        self.score_t.draw(screen)
        self.enemy.draw(screen)
        self.enemy2.draw(screen)

    def move(self):
        '''
        Runs balls' and gun's movement method, removes dead balls.
        '''
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        self.gun.gain()
        self.enemy.update()
        self.enemy2.update()

    def collide(self):
        '''
        Checks whether balls bump into targets, sets balls' alive trigger.
        '''
        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)


screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun of Khiryanov")

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=3)

while not done:
    clock.tick(15)
    screen.fill(PURPLE)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()


pg.quit()
