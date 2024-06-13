from kivy.uix.actionbar import BoxLayout
from kivymd.uix.filemanager.filemanager import FitImage
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screenmanager import ScreenManager #, Screen
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivy.clock import Clock
from kivymd.uix.navigationrail import MDNavigationRailItem
from kivy.uix.pagelayout import PageLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.image import Image as KvImage
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import pickle
import bz2
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config

from copy import deepcopy

import image_process
import img_processor

import toml

import kivymd.icon_definitions

import gc
import cv2
import numpy as np
import math
import json
import time
import os
import sys

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from kivy.uix.button import Button

COLOR_PICKER_GLOBAL = (0, 0, 0, 1)

color_picker = (0, 0, 0, 1)
gl_save_count = 0

#! デバッグ用モード切替
#! 0:塗りつぶしモード
#! 1:描画モード
write_mode = 1

def tag_index_find(l, x):
    return l.index(x) if x in l else -1



class PainterScreen(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.color_picker = (0, 0, 0, 1)
        self.drawing = False
        self.stroke = []
        self.undo_strokes = []
        self.color_history = []
        self.save_count = 0
        self.image_history = [] 
        self.load_state = False
        self.final_shape = []
        self.color_changer_count = 1
        self.color_changer_count_rv = False
        self.color_change_number = []
        self.tmp_count = 0
        Window.bind(on_motion=self.on_motion)
        Window.bind(on_keyboard=self.on_keyboard)
        self.line_width = 20

        self.nurie_data = []
        self.list_nurie_page = []
        
        self.float_layout = FloatLayout()
        self.float_layout.add_widget(
            MDBoxLayout(
                Button(
                    text = '<',
                    ),
                MDBoxLayout(
                    id = "page_layout",
                    orientation="horizontal",
                    ),
                Button(
                    text = '>',
                    ),
                orientation = 'horizontal',
                    
                ),
        )
        
        self.page_id = self.ids.page_layout
        self.nurie_sm = ScreenManager()
        nurie_dir = "./nurie"
        ext = (".png", ".jpg", ".jpeg",".PNG", ".JPG", ".JPEG","webp")
        for root, dirs, files in os.walk(nurie_dir):
            for file in files:
                self.nurie_data.append(file)

        max_img = 8
        page_count = math.ceil(len(self.nurie_data) / max_img) + 1
        print(page_count)
        for i in range(page_count):
            print(i)


        


        grid = MDGridLayout(cols=4, rows=2)

        for i in range(len(self.tag_list)):
            print(self.tag_list[i])

            grid.add_widget(
                MDCard(
                    MDRelativeLayout(
                        FitImage(
                            source = "./nurie/" + self.tag_list[i] + "/preview.jpg",
                            pos_hint = {"top": 1},
                            radius = "12dp", 

                        ),
                        MDLabel(
                            text = self.tag_list[i],
                            adaptive_size=True,
                            color = "grey",
                        ),
                    
                    ),
                    style="elevated",
                    padding="4dp",
                    size_hint=(1, 1),
                    ripple_behavior=True,
                    on_press=lambda x, tag=self.tag_list[i], list=self.img_list[i]: self.update_select_screen(tag,list),                        
                )
            )
        
        
        grid.add_widget(
            MDCard(
                
                MDLabel(
                    text = "back",
                    adaptive_size=True,
                    color = "grey",
                ),
                style="elevated",
                padding="4dp",
                size_hint=(1, 1),
                ripple_behavior=True,
                on_press=lambda x: self.float_layout.clear_widgets(),                        
            )
        )
        
        
        
        self.float_layout.add_widget(grid)
        self.add_widget(self.float_layout)

        
        
        
    def on_motion(self,*args):
        if self.drawing:
            if args[1] == "update":
                pos = args[2]
                pos = (int(pos.spos[0] * Window.width), int(pos.spos[1] * Window.height))
                self.on_image_mouse(pos)
    
    def update_select_screen(self,id,img_list):
        print(id)
        print(img_list)
        
        self.float_layout.clear_widgets()
        
        
        grid = MDGridLayout(cols=4, rows=5)

        for i in range(len(img_list)):
            print(img_list[i])

            grid.add_widget(
                MDCard(
                    MDRelativeLayout(
                        FitImage(
                            source = "./nurie/" + id + "/" + img_list[i] + ".png",
                            pos_hint = {"top": 1},
                            radius = "12dp", 

                        ),
                        MDLabel(
                            text = img_list[i],
                            adaptive_size=True,
                            color = "grey",
                        ),
                    
                    ),
                    style="elevated",
                    padding="4dp",
                    size_hint=(1, 1),
                    ripple_behavior=True,
                    on_press=lambda x, id=id + "/" + img_list[i] + ".png": self.load_nurie_data(id),                        
                )
            )
        
        self.float_layout.add_widget(grid)

    def on_image1_down(self, touch):
        if write_mode == 0:
            if self.collide_point(*touch.pos):
                self.fill(touch)
        else:
            if self.collide_point(*touch.pos):
                if self.drawing == False:
                    self.drawing = True
                else:
                    self.drawing = False

    def on_image1_move(self, touch):
        pass
    
    def on_image_mouse(self, touch):
        if write_mode == 0:
            pass
        else:
            if self.drawing:
                
                try:
                    process_texture, self.cood_hist = image_process.image_process(self.color_img, self.gray_img, touch, self.cood_hist, Window, self.line_width)
                    self.gray_img = process_texture
                    texture_canvas = Texture.create(size=(process_texture.shape[1], process_texture.shape[0]), colorfmt='bgr')
                    texture_canvas.blit_buffer(process_texture.tobytes(), colorfmt='bgr')
                    self.canvas.clear()
                    with self.canvas:
                        Rectangle(texture=texture_canvas, pos=(0, 0), size=(process_texture.shape[1], process_texture.shape[0]))
                except:
                    self.cood_hist = int(touch[0]), int(touch[1])
                    process_texture , self.cood_hist = image_process.image_process(self.color_img, self.gray_img, touch, self.cood_hist, Window, self.line_width)   
                    self.gray_img = process_texture
                    texture_canvas = Texture.create(size=(process_texture.shape[1], process_texture.shape[0]), colorfmt='bgr')
                    texture_canvas.blit_buffer(process_texture.tobytes(), colorfmt='bgr')
                    self.canvas.clear()
                    with self.canvas:
                        Rectangle(texture=texture_canvas, pos=(0, 0), size=(process_texture.shape[1], process_texture.shape[0]))

                
    def on_image1_up(self, touch):
        if write_mode == 0:
            if self.drawing:
                self.drawing = False
                self.stroke.append(touch.ud['image'])
            #print(self.image_history)
        else:
            try:
                del self.cood_hist
            except:
                pass

    def load_nurie_data(self,id):
        
        
        self.float_layout.clear_widgets()
        
        
        self.raw_img = "pre3.png"
        
        
        file = cv2.imread(self.raw_img, 1)
        
        
        """
        c_width = int(self.ids.main_canvas.width)
        c_height = int(self.height)
        """
        
        c_width = int(Window.width)
        c_height = int(Window.height)
        
        print("c_width:" + str(c_width))
        print("c_height:" + str(c_height))
        
        try:
            print(str(file.shape[0])) # 縦
            print(str(file.shape[1])) # 横
        except:
            return
        mag_height = c_height / file.shape[0]
        mag_width = c_width / file.shape[1]
        
        if mag_height < mag_width:
            mag = mag_height
            aspect_mode = "height"
        else:
            mag = mag_width
            aspect_mode = "width"
        
        
        c_width = int(file.shape[1] * mag)
        c_height = int(file.shape[0] * mag)
        
        
        
        res_img = cv2.resize(file, dsize = (c_width, c_height))

        self.color_img = res_img
        
        self.gray_img = img_processor.img_prosessor(self.raw_img)
        self.gray_img = np.stack((self.gray_img,)*3, axis=-1)
        self.gray_img = cv2.resize(self.gray_img, dsize = (c_width, c_height))

        width_while = (int(Window.width/2 - self.gray_img.shape[1]/2))
        height_while = (int(Window.height/2 - self.gray_img.shape[0]/2))

        full_img = np.full((Window.height, Window.width),255, dtype=np.uint8)
        full_img = np.stack((full_img,)*3, axis=-1)
        if aspect_mode == "height":
            dx = width_while   # 横方向の移動距離
            dy = 0    # 縦方向の移動距離
        else:
            dx = 0
            dy = height_while
        h, w = self.gray_img.shape[:2]
        full_img[dy:dy+h, dx:dx+w] = self.gray_img
        

        cv2.imwrite('nurie.png', full_img)

        self.gray_img = cv2.flip(self.gray_img, 0)
        self.color_img = cv2.flip(self.color_img, 0)

        full_img = np.full((Window.height, Window.width),255, dtype=np.uint8)
        full_img = np.stack((full_img,)*3, axis=-1)
        

        
        h, w = self.gray_img.shape[:2]
        full_img[dy:dy+h, dx:dx+w] = self.gray_img
        self.gray_img = full_img

        
        full_img = np.full((Window.height, Window.width),255, dtype=np.uint8)
        full_img = np.stack((full_img,)*3, axis=-1)
        if aspect_mode == "height":
            dx = width_while   # 横方向の移動距離
            dy = 0    # 縦方向の移動距離
        else:
            dx = 0
            dy = height_while
        h, w = self.color_img.shape[:2]
        full_img[dy:dy+h, dx:dx+w] = self.color_img
        self.color_img = full_img
        
        cv_image = CoreImage.load("./nurie.png")
        cv_image = cv_image.texture
        
        with self.canvas:
            Rectangle(texture=cv_image, pos=(0, 0), size=(Window.width, Window.height))
        
        
        self.load_state = True
        
        
    def on_keyboard(self, instance, key, scancode, codepoint, modifiers):
        print(key)
        if key == 273:
            if self.line_width < 50:
                self.line_width += 1
        elif key == 274:
            if self.line_width > 2:
                self.line_width -= 1


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Olive"  # "Purple", "Red"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PainterScreen(name='painter'))
        return sm
    
    def on_resume(self, *args):
        self.theme_cls.set_colors()

    def set_dynamic_color(self, *args) -> None:
        self.theme_cls.dynamic_color = True
        
    def on_stop(self):
        global gl_save_count
        print(gl_save_count)
        for i in range(gl_save_count):
            os.remove("./tmp/" + str(i) + "imga.png")
        try:
            os.remove('temp.png')
        except:
            pass
        try:
            os.remove('temp2.png')
        except:
            pass
        try:
            os.remove('temp3.png')
        except:
            pass
        try:
            os.remove('nurie.png')
        except:
            pass

if __name__ == '__main__':
    MainApp().run()