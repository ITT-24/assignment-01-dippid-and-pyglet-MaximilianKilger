import pyglet
import sys, os, math, random
from DIPPID import SensorUDP
import numpy as np

WIN_WIDTH:int = 700
WIN_HEIGHT:int = 700

HEAD_TEXTURE_PATH:str = os.path.join("sprites", "head_placeholder.png")
BODY_TEXTURE_PATH:str = os.path.join("sprites", "body_placeholder.png")
FOOD_TEXTURE_PATH:str = os.path.join("sprites", "food_placeholder.png")

HEAD_SIZE:int = 20
FOOD_SIZE:int = 18
BODY_SEGMENT_SIZE:int = 15

window = pyglet.window.Window(WIN_WIDTH,WIN_HEIGHT)

#returns the euclidian distance between points (x1, y1) and (x2, y2)
def euclidian(pos1:tuple[float,float], pos2:tuple[float,float]):
    return math.sqrt( (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

class Circle ():
    def __init__(self, xpos:float, ypos:float, radius:int):
        # the coordinates of the circle's center. Please avoid setting them directly, use the move() function.
        self.xpos = xpos
        self.ypos = ypos 

        self.radius = radius

        self.sprite = pyglet.shapes.Circle(xpos,ypos,radius, color =(255,0,255))

    def move(self, delta_x:float, delta_y:float, ignore_collision:bool=False):
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
    
    # for some reason not supported by python type hinting in VS Code, 
    # but other_circle is supposed to be an instance of the Circle class.
    def check_collision_with_circle(self, other_circle) -> bool:

        eucl_dist = euclidian(self.get_coordinates(), other_circle.get_coordinates())
        return eucl_dist < self.radius + other_circle.radius

    # places this circle along the line between its center and another circle's center
    # so that it intersects the other circle in only one point.
    # again, other_circle is supposed to be a circle.
    def place_tangentially_to(self,other_circle):
        other_xpos, other_ypos = other_circle.get_coordinates()
        other_radius = other_circle.get_radius()
        
        current_delta_x = self.xpos - other_xpos
        current_delta_y = self.ypos - other_ypos

        distance = euclidian(other_circle.get_coordinates(), self.get_coordinates())
        if distance > 0:
            distance_to_move = distance - (other_radius + self.radius)
            delta_x = current_delta_x / distance * distance_to_move
            delta_y = current_delta_y / distance * distance_to_move

            self.move(-delta_x, -delta_y, ignore_collision=True)
            #self.xpos -= delta_x
            #self.ypos -= delta_y
            #self.sprite.x = self.xpos
            #self.sprite.y = self.ypos
            #self.check_collision_with_wall()

    def draw(self):
        self.sprite.draw()

    def get_coordinates(self)-> tuple[float, float]:
        return self.xpos, self.ypos
    
    def get_radius(self) -> int:
        return self.radius


class Head(Circle):

    def __init__(self, xpos:float, ypos:float, radius:int, rotation:float=0):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        self.rotation = rotation

        texture = pyglet.image.load(HEAD_TEXTURE_PATH)
        #move texture's anchor point to the center
        texture.anchor_x = texture.width//2
        texture.anchor_y = texture.height//2

        self.sprite = pyglet.sprite.Sprite(texture, x=xpos, y=ypos)
        self.sprite.width = self.radius*2
        self.sprite.height = self.radius*2
        self.sprite.rotation = rotation

        self.first_body_segment:BodySegment = None
    
    def move(self, delta_x:float, delta_y:float, ignore_collision:bool=False):
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
            self.rotation = angle
            self.sprite.rotation = np.rad2deg(angle)
        if self.first_body_segment != None:
            self.first_body_segment.place_tangentially_to(self)


    
    def add_segment(self):
        if self.first_body_segment == None:
            distance = self.radius + BODY_SEGMENT_SIZE
            delta_x = np.sin(self.rotation) * -distance 
            delta_y = np.cos(self.rotation) * -distance 
            #if not 0 < self.rotation < np.pi:
            #    delta_x *= -1
            #    delta_y *= -1
            
            print(delta_x, delta_y)

            self.first_body_segment = BodySegment(self.xpos + delta_x, self.ypos + delta_y, BODY_SEGMENT_SIZE, self.rotation)
        else:
            self.first_body_segment.add_segment()

    def draw(self):
        self.sprite.draw()
        if self.first_body_segment != None:
            self.first_body_segment.draw()
    
    def check_collision_with_head(self):
        if self.first_body_segment != None:
            return self.first_body_segment.check_collision_with_head(self)
        else:
            return False

    # generator function to iterate through all body segments.
    def get_all_body_segments(self):
        current_segment = self.first_body_segment
        while current_segment != None:
            yield current_segment
            current_segment = current_segment.next_segment



class BodySegment(Circle):
    def __init__(self, xpos:float, ypos:float, radius:int, rotation:float=0):
        self.xpos:float = xpos
        self.ypos:float = ypos
        self.radius:int = radius
        self.rotation:float = rotation #from -2*pi to 2*pi

        texture = pyglet.image.load(BODY_TEXTURE_PATH)
        #move texture's anchor point to the center
        texture.anchor_x = texture.width//2
        texture.anchor_y = texture.height//2

        self.sprite = pyglet.sprite.Sprite(texture, x=xpos, y=ypos)
        self.sprite.width = self.radius*2
        self.sprite.height = self.radius*2

        self.next_segment:BodySegment = None
    
    def draw(self):
        self.sprite.draw()
        if self.next_segment != None:
            self.next_segment.draw()

    def move(self, delta_x:float, delta_y:float, ignore_collision:bool=False):
        
        super().move(delta_x, delta_y)
        try:
            angle = np.arctan2(delta_x , delta_y)
        except ZeroDivisionError:
            angle = np.pi/2
        if delta_y > 0:
            angle += np.pi
        self.rotation = angle
        self.sprite.rotation = np.rad2deg(angle)
        if not ignore_collision:
            for segment in gameManager.head.get_all_body_segments():
                if not (segment is self.next_segment or segment.next_segment is self):
                    if self.check_collision_with_circle(segment):
                        self.place_tangentially_to(segment)
        if self.next_segment == None:
            return
        self.next_segment.place_tangentially_to(self)

    def add_segment(self):
        if self.next_segment != None:
            self.next_segment.add_segment()
        else:
            distance = self.radius + BODY_SEGMENT_SIZE
            delta_x = np.sin(self.rotation) * -distance 
            delta_y = np.cos(self.rotation) * -distance 
            if 0 < self.rotation < np.pi:
                delta_x *= -1
                delta_y *= -1
            
            self.next_segment = BodySegment(self.xpos + delta_x, self.ypos + delta_y, BODY_SEGMENT_SIZE, self.rotation)
            for segment in gameManager.head.get_all_body_segments():
                if not segment is self:
                    if self.next_segment.check_collision_with_circle(segment):
                        print("Self-intersection rule applied")
                        delta_x *= -1
                        delta_y *= -1
                        self.next_segment = BodySegment(self.xpos + delta_x, self.ypos + delta_y, BODY_SEGMENT_SIZE, (self.rotation + np.pi) % (2*np.pi))
                        break
    def check_collision_with_head(self, head:Head):
        if not head.first_body_segment is self:
            if self.check_collision_with_circle(head):
                return True
        if self.next_segment == None:
            return False
        else:
            return self.next_segment.check_collision_with_head(head)


            
            


    
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
        self.reset()
        self.paused:bool = False

    def reset(self):
        self.head = Head(window.width/2, window.height/2, HEAD_SIZE)
        self.foods:list[Food] = []
        self.score:int = 0
        self.spawn_food()

    def update(self):
        if self.paused:
            return
        self.check_snake_eats_itself()
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
        if self.paused:
            return

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
                self.head.add_segment()
                break
    def check_snake_eats_itself(self):
        if self.head.check_collision_with_head():
            self.reset()
            
            #self.paused = True


gameManager = GameManager()

@window.event
def on_key_press(symbol, modifiers):
    rate_acc = 0.5
    if symbol == pyglet.window.key.Q:
        os._exit(0)
    elif symbol == pyglet.window.key.P:
        gameManager.paused = not gameManager.paused
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
