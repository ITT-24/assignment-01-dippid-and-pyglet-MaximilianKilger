import pyglet
import sys, os, math, random
from DIPPID import SensorUDP
import numpy as np

WIN_WIDTH = 700
WIN_HEIGHT = 700

HEAD_TEXTURE_PATH = os.path.join("sprites", "head_placeholder.png")
BODY_TEXTURE_PATH = os.path.join("sprites", "body_placeholder.png")
FOOD_TEXTURE_PATH = os.path.join("sprites", "food_placeholder.png")

HEAD_SIZE = 20
FOOD_SIZE = 15

window = pyglet.window.Window(WIN_WIDTH,WIN_HEIGHT)

class Circle ():
    def __init__(self, xpos:float, ypos:float, radius:int):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        self.sprite = pyglet.shapes.Circle(xpos,ypos,radius, color =(255,0,255))

    def move(self, delta_x:float, delta_y:float):
        self.xpos  += delta_x
        self.ypos += delta_y
        self.sprite.x = self.xpos
        self.sprite.y = self.ypos
        self.check_collision_with_wall()
    
    def check_collision_with_wall(self):
        if self.xpos - self.radius < 0:
            self.xpos = self.radius
        elif self.xpos + self.radius > window.width:
            self.xpos = window.width - self.radius
        if self.ypos - self.radius < 0: 
            self.ypos = self.radius
        elif self.ypos + self.radius > window.height:
            self.ypos = window.height - self.radius
    
    def check_collision_with_circle(self, other_circle) -> bool:
        diff_x = abs(self.xpos - other_circle.xpos)
        diff_y = abs(self.ypos - other_circle.ypos)

        eucl_dist = math.sqrt(diff_x**2 + diff_y**2)

        return eucl_dist < self.radius + other_circle.radius

    def draw(self):
        self.sprite.draw()

class Head(Circle):

    def __init__(self, xpos:float, ypos:float, radius:int, orientation:float = 0):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        texture = pyglet.image.load(HEAD_TEXTURE_PATH)
        texture.anchor_x = texture.width//2
        texture.anchor_y = texture.height//2
        self.sprite = pyglet.sprite.Sprite(texture, x=xpos, y=ypos)
        self.sprite.width = self.radius*2
        self.sprite.height = self.radius*2
    
    def move(self, delta_x:float, delta_y:float):
        DEADZONE_ANGLE = 0.15
        super().move(delta_x, delta_y)
        if math.sqrt(delta_x**2 + delta_y**2) > DEADZONE_ANGLE:
            if delta_y == 0:
                delta_y = 0.000001
            try:
                angle = np.arctan(delta_x / delta_y)
            except ZeroDivisionError:
                angle = np.pi/2
            if delta_y < 0:
                angle += np.pi
            self.sprite.rotation = np.rad2deg(angle)
    
class Food(Circle):

    def __init__(self, xpos:float, ypos:float, radius:int):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        texture = pyglet.image.load(FOOD_TEXTURE_PATH)
        texture.anchor_x = texture.width//2
        texture.anchor_y = texture.height//2
        self.sprite = pyglet.sprite.Sprite(texture, x=xpos, y=ypos)
        self.sprite.width = self.radius*2
        self.sprite.height = self.radius*2
        

    

PORT = 5700
sensor = SensorUDP(PORT)

def get_sensor_data():
    if sensor.has_capability('accelerometer'):
        strength = -5
        acc_x = np.sin(sensor.get_value('accelerometer')['x']) * strength
        acc_y = np.sin(sensor.get_value('accelerometer')['y']) * strength
        gameManager.handle_movement(acc_x, acc_y)

class GameManager():
    def __init__(self):
        self.head = Head(window.width/2, window.height/2, HEAD_SIZE)
        self.foods = []
        self.score = 0
        self.spawn_food()

    def update(self):
        self.check_food()

    def render(self):
        for food in self.foods:
            food.draw()
            
        self.head.draw()

    def spawn_food(self):
        xpos = random.randrange(FOOD_SIZE, window.width-FOOD_SIZE)
        ypos = random.randrange(FOOD_SIZE, window.height-FOOD_SIZE)
        food = Food(xpos, ypos, FOOD_SIZE)
        self.foods.append(food)


    def handle_movement(self,acc_x:float, acc_y:float):

        DEADZONE = 0.1
        delta_x, delta_y = 0,0
        if abs(acc_x) > DEADZONE:
            delta_x = acc_x
        if abs(acc_y) > DEADZONE:
            delta_y = acc_y
        self.head.move(delta_x, delta_y)
    
    def check_food(self):
        for food in self.foods:
            if self.head.check_collision_with_circle(food):
                print("Munch")
                self.score += 1
                self.foods.remove(food)
                self.spawn_food()
                break

gameManager = GameManager()

@window.event
def on_key_press(symbol, modifiers):
    rate_acc = 0.5
    if symbol == pyglet.window.key.Q:
        os._exit(0)
    elif symbol == pyglet.window.key.UP:
        gameManager.head.move(0,rate_acc)
    elif symbol == pyglet.window.key.DOWN:
        gameManager.head.move(0,-rate_acc)
    elif symbol == pyglet.window.key.LEFT:
        gameManager.head.move(-rate_acc,0)
    elif symbol == pyglet.window.key.RIGHT:
        gameManager.head.move(rate_acc,0)


        

@window.event
def on_draw():
    get_sensor_data()
    gameManager.update()
    window.clear()
    gameManager.render()
    
pyglet.app.run()
