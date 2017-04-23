from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.graphics import Line
from kivy.clock import Clock
from kivy.properties import NumericProperty

WIDTH=Window.width
HEIGHT=Window.height

class LeftButton(Button):
    pass
class RightButton(Button):
    pass
class StrideSlider(Slider):
    pass
class PaceSlider(Slider):
    pass

class LegsApp(App):
    def build(self):
        return MainWindow()

class MainWindow(Widget):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.height = HEIGHT
        self.width = WIDTH
        self.legs=Legs()
        self.slider_box = BoxLayout(width = WIDTH, height = HEIGHT * 0.2, top=HEIGHT)
        self.btn_box = BoxLayout(width = WIDTH, height = HEIGHT * 0.2, top=HEIGHT * 0.8)
        self.stride_slider = StrideSlider(min=1, max=50,value=20)
        self.stride_slider.bind(value=self.set_stride)
        self.slider_box.add_widget(self.stride_slider)
        self.speed_slider = PaceSlider(min=1, max=100, value=20)
        self.speed_slider.bind(value = self.set_speed)
        self.slider_box.add_widget(self.speed_slider)
        self.left_btn = LeftButton()
        self.right_btn = RightButton ()
        self.left_btn.bind(on_press = self.legs.go_left)
        self.right_btn.bind(on_press = self.legs.go_right)
        self.left_btn.bind(on_release = self.legs.stop_walking)
        self.right_btn.bind(on_release = self.legs.stop_walking)
        self.btn_box.add_widget(self.left_btn)
        self.btn_box.add_widget(self.right_btn)
        self.add_widget(self.slider_box)
        self.add_widget(self.btn_box)
        self.add_widget(self.legs)

    def set_stride(self,instance, value):
        self.legs.stride = value

    def set_speed(self, instance, value):
        self.legs.speed = value
    
class Legs(Widget):
    stride = NumericProperty(20)
    speed = NumericProperty(20)
    def __init__(self, **kwargs):
        super(Legs, self).__init__(**kwargs)
        self.left_leg=Leg(right=False)
        self.right_leg=Leg(right=True)
        self.add_widget(self.right_leg)
        self.add_widget(self.left_leg)
        self.going_right = True
        
    def go_left(self, instance):
        self.going_right = False
        self.start_walking()
        
    def go_right(self, instance):
        self.going_right = True                   
        self.start_walking()
    
    def start_walking(self):
        Clock.schedule_interval(self.left_leg.walk, 0.1 / int(self.speed))
        Clock.schedule_interval(self.right_leg.walk, 0.1 / int(self.speed))

    def stop_walking(self, instance):
        Clock.unschedule(self.left_leg.walk)
        Clock.unschedule(self.right_leg.walk)
        self.left_leg.stance()
        self.right_leg.stance()
    
# x1 and y1 is a vector used for calculating the position of the knee
# x2 and y2 is used for the foot.
class Leg(Widget):
    hip_x=NumericProperty(400)
    hip_y=NumericProperty(300)
    knee_x=NumericProperty(400)
    knee_y=NumericProperty(200)
    foot_x=NumericProperty(400)
    foot_y=NumericProperty(100)
    x1=NumericProperty(0)
    y1=NumericProperty(100)
    x2=NumericProperty(0)
    y2=NumericProperty(100)    
    
    def __init__(self, **kwargs):
        super(Leg, self).__init__(**kwargs)
        self.size = Window.size
        # Rotational direction and speed of the upper leg
        self.femur_clockwise=True
        self.femur_speed = 1
        # Rotational direction and speed of the lower leg
        self.tibia_clockwise=True
        self.tibia_speed = 1
        # Is this the right leg?
        self.right = kwargs['right']
        # Count is used for calculating the position of the entire leg.
        self.count = None
        self.stance()

    def stance(self, *args):
        self.knee_x, self.knee_y = (400,200)
        self.foot_x, self.foot_y = (400,100)
        # A leg consists of two vectors in continuation of each other, each with a length of 100 px.
        # When stance is called the right leg is set to follow a straight line 10 degrees clockwise from the y-axis,
        # and the left leg is mirrored at the y-axis.
        if self.right:
            self.x1,self.y1 = Vector(0,100).rotate(10)
        else:
            self.x1,self.y1 = Vector(0,100).rotate(-10)
        self.x2,self.y2 = self.x1, self.y1
        self.count = 0       
        self.draw_leg()

        
    def walk(self,*args,**kwargs):
        mod = int(self.parent.stride)
        if self.count == 6 * mod:
            self.count = 0
        phase = self.count
        if not self.right:
            phase = (self.count + 3 * mod) % (6 * mod)
            
        if 0 <= phase < 1 * mod:
            self.femur_clockwise = True
            self.femur_speed = 1
            self.tibia_clockwise = True
            self.tibia_speed = 1
        if 1 * mod <= phase < 2 * mod:
            self.femur_clockwise = True
            self.femur_speed = 1
            self.tibia_clockwise = False
            self.tibia_speed = 2
        if 2 * mod <= phase < 3 * mod:
            self.femur_clockwise = False
            self.femur_speed = 2
            self.tibia_clockwise = True
            self.tibia_speed = 1
        if 3 * mod <= phase < 4 * mod:
            self.femur_clockwise = False
            self.femur_speed = 1
            self.tibia_clockwise = False
            self.tibia_speed = 1
        if 4 * mod <= phase < 5 * mod:
            self.femur_clockwise = False
            self.femur_speed = 1
            self.tibia_clockwise = False
            self.tibia_speed = 2
        if 5 * mod <= phase < 6 * mod:
            self.femur_clockwise = True
            self.femur_speed = 2
            self.tibia_clockwise = True
            self.tibia_speed = 3
            
        if not self.parent.going_right:
            self.femur_clockwise = not self.femur_clockwise
            self.tibia_clockwise = not self.tibia_clockwise
        
        if self.femur_clockwise:
            self.x1,self.y1=Vector((self.x1,self.y1)).rotate(self.femur_speed)
        if not self.femur_clockwise:
            self.x1,self.y1=Vector((self.x1,self.y1)).rotate(-self.femur_speed)
        if self.tibia_clockwise:
            self.x2,self.y2=Vector((self.x2,self.y2)).rotate(self.tibia_speed)
        if not self.tibia_clockwise:
            self.x2,self.y2=Vector((self.x2,self.y2)).rotate(-self.tibia_speed)
        self.count += 1
        self.draw_leg()
        
    def draw_leg(self):
        self.knee_x = self.hip_x-self.x1
        self.knee_y = self.hip_y-self.y1
        self.foot_x = self.knee_x-self.x2
        self.foot_y = self.knee_y-self.y2
        self.canvas.clear()
        with self.canvas:
            Color=(1,0,0)
            Line(points=[self.hip_x,self.hip_y,self.knee_x,self.knee_y,self.foot_x,self.foot_y],width=10)

            
if __name__=="__main__":
    LegsApp().run()
    
