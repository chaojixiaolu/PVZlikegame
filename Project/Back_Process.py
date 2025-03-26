import pygame
import random
import os
from Load_image import *

screen_width = 800
screen_height = 600

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)  
RED = (255, 0, 0) 
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHTBLUE = (173, 216, 230)
YELLOW = (255, 255, 0)

# グリッド設定
GRID_HEIGHT = 80
GRID_WIDTH = 80
GRID_V_Number = 5
GRID_C_Number = 10

# **各グリッドの左上座標**
GRID_V = [GRID_HEIGHT * i + 180 for i in range(GRID_V_Number)]
GRID_C = [GRID_WIDTH * i for i in range(GRID_C_Number)]

# **各グリッドの中心座標**
GRID_CENTER = [[(GRID_C[i] , GRID_V[j]) 
                for j in range(GRID_V_Number)] 
                for i in range(GRID_C_Number)]

def get_grid_center(mouse_x, mouse_y): #マス目対応
    for i in range(GRID_C_Number):
        for j in range(GRID_V_Number):
            if GRID_C[i] <= mouse_x < GRID_C[i] + GRID_WIDTH and GRID_V[j] <= mouse_y < GRID_V[j] + GRID_HEIGHT:
                return GRID_CENTER[i][j]  # グリッドの中心座標を返す
    return None  # 該当するグリッドがない場合



def draw_background():
    bg_surface = pygame.Surface((screen_width, screen_height))
    bg_surface.fill(WHITE)
    
    for i in range(GRID_C_Number):
        pygame.draw.line(bg_surface, BLACK, (GRID_C[i], 180), (GRID_C[i], 500))

    for j in range(GRID_V_Number):
        pygame.draw.line(bg_surface, BLACK, (0, GRID_V[j]), (screen_width, GRID_V[j]))

    return bg_surface


class Error(pygame.sprite.Sprite):
    def __init__(self, screen, text):
        super().__init__()
        self.screen = screen  # 画面参照
        self.font = pygame.font.SysFont(None, 30)
        self.text_message = self.font.render(text, True, RED)
        self.rect = self.text_message.get_rect(center=(400, 300))  # 画面の中央に配置
        self.show_time = pygame.time.get_ticks()

    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time > self.show_time + 1000:
            self.kill()
    
    def draw(self, screen):
        """ メッセージを画面に描画 """
        screen.blit(self.text_message, self.rect)

#ぼたん

class Plantbutton(pygame.sprite.Sprite):
    def __init__(self, instance):
        super().__init__()
        self.color = GREEN
        self.center = (80, 20)
        self.instance = instance
        self.image = pygame.Surface((80, 40))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=self.center)
        instance.buttons.add(self)
        self.mode = "Plant"
        self.draw()

    def draw(self):
        self.cost = globals().get(f"{self.mode}_cost")
        self.text = self.instance.font.render(f"{self.cost}", True, BLACK)
        self.text_rect = self.text.get_rect(center=(40,20))
        self.image.blit(self.text, self.text_rect)

    def Process(self):
        self.instance.selected_plant = self.mode
    
class Rockbutton(Plantbutton):
    def __init__(self, instance):
        super().__init__(instance)
        self.color = BROWN
        self.center = (160, 20)
        self.image.fill(self.color)  # 色を更新
        self.rect = self.image.get_rect(center=self.center)  # 位置を更新
        self.mode = "Rock"
        self.draw()

class Firebutton(Plantbutton):
    def __init__(self, instance):
        super().__init__(instance)
        self.color = ORANGE
        self.center = (240, 20)
        self.image.fill(self.color)  # 色を更新
        self.rect = self.image.get_rect(center=self.center)  # 位置を更新
        self.mode = "Fire"
        self.draw()

class Waterbutton(Plantbutton):
    def __init__(self, instance):
        super().__init__(instance)
        self.color = LIGHTBLUE
        self.center = (320, 20)
        self.image.fill(self.color)  # 色を更新
        self.rect = self.image.get_rect(center=self.center)  # 位置を更新
        self.mode = "Water"
        self.draw()

class Thunderbutton(Plantbutton):
    def __init__(self, instance):
        super().__init__(instance)
        self.color = YELLOW
        self.center = (400, 20)
        self.image.fill(self.color)  # 色を更新
        self.rect = self.image.get_rect(center=self.center)  # 位置を更新
        self.mode = "Thunder"
        self.draw()

class PauseButton(pygame.sprite.Sprite):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance
        self.image = pygame.Surface((80, 40))
        self.image.fill((200, 200, 200))  # グレー
        self.font = pygame.font.Font(None, 30)
        self.text = self.font.render("Pause", True, (0, 0, 0))
        self.rect = self.image.get_rect(topright=(790, 10))
        instance.buttons.add(self)

    def Process(self):
        self.instance.paused = not self.instance.paused  # 一時停止状態を切り替える

#

class LevelupButton(pygame.sprite.Sprite):
        def __init__(self, plant, upper_class, instance):
            super().__init__()
            self.upper_class = upper_class
            self.rect = pygame.Rect(455 ,475, 90, 45)
            self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)  # 透明対応
            self.plant = plant

            self.screen = plant.screen
            self.instance = instance
            instance.buttons.add(self)
            plant.button_sprites.add(self)
            
        def Process(self):
            self.current_point = self.instance.points
            if item_consume(self.instance.plant_cost, self.instance.plant_items, self.instance):
                self.new_plant = self.upper_class(self.plant.rect.x, self.plant.rect.y, self.instance)
                self.plant.kill()
                self.instance.all_sprites.add(self.new_plant)
                self.instance.plants.add(self.new_plant)

                # **ズームアウトを開始する前にスプライトを削除しない**
                self.instance.start_zoom_out()

                # **ズームアウト開始後にスプライトを削除**
                for sprite in list(self.plant.button_sprites):  # 明示的にリスト化
                    sprite.kill()
                    del sprite

        
        def update(self):
            if not self.plant.alive():  # 親が生存しているかチェック
                self.kill()  # 自分も削除
        
class noLevelupButton(pygame.sprite.Sprite):
            def __init__(self, plant, instance):
                super().__init__()
                self.rect = pygame.Rect(550, 475, 200, 45)
                self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)  # 透明対応
                self.plant = plant
                self.screen = plant.screen
                self.instance = instance
                instance.buttons.add(self)
                plant.button_sprites.add(self)
            
            
            def Process(self):
                self.plant.leveluptext = False

                # **ズームアウトを開始**
                self.instance.start_zoom_out()

                # **ズームアウト開始後にスプライトを削除**
                for sprite in list(self.plant.button_sprites):
                    sprite.kill()
                    del sprite


            def update(self):
                if not self.plant.alive():  # 親が生存しているかチェック
                    self.kill()  # 自分も削除
                      
#描写処理

def draw_hp(screen, plant, Color):
        """HPバーをプラントの上に描画"""
        bar_x = plant.rect.x
        bar_y = plant.rect.y - 10  # ゾンビの上に配置
        hp_ratio = plant.hp / plant.max_hp  # HPの割合
        hp_width = int(plant.hp_bar_width * hp_ratio)  # HPバーの現在の長さ
        plant.screen = screen

        # HPバーの枠（黒）
        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, plant.hp_bar_width + 2, 6))
        # HPバーの本体（緑）
        pygame.draw.rect(screen, Color, (bar_x, bar_y, hp_width, 4))

def draw_level(screen, plant, Color):
    text_image = plant.font.render(f"Level:{plant.level}", True, Color)  
    screen.blit(text_image, (plant.rect.x, plant.rect.y - 25))

def drawart(screen, animation, pos, name, tag):
    art = art_dict[name]
    pos_x, pos_y = pos
    if animation:
        # アニメーションを描画
        if art.image:
            frame = art.image[tag]  # 現在のフレームを選択
            screen.blit(frame, (pos_x - art.art_dif_x, pos_y - art.art_dif_y))  # アニメーションフレームを描画
        else:
            print("No animation frames to draw!")
        tag = (tag + 1) % art.frames
    else:
        screen.blit(art.image[0], (pos_x - art.art_dif_x, pos_y - art.art_dif_y))
    return tag

#Character処理

class DropItemText(pygame.sprite.Sprite):
    def __init__(self, item_name, number,  pos, instance):
        super().__init__()
        self.instance = instance
        self.item_name = item_name  # ドロップしたアイテムの名前
        self.rect_x,  self.rect_y = pos
        self.alpha = 255  # 透明度
        self.life_time = 60  # 60フレーム（1秒）で消える
        self.font = pygame.font.Font(None, 24)

        if not item_name == "points":
            self.image = item_image_dict.get(f"{item_name}_image", None)  # アイテムの画像
            self.text_image = self.font.render(f"x{number}", True, (255, 255, 255))  # "×1" のテキスト
        else:
            self.text_image = self.font.render(f"points +{number}", True, (255, 255, 255))


    def update(self):
        """ アイテムを上に浮かせ、徐々に透明にする """
        self.rect_y -= 1  # 1フレームごとに上へ移動
        self.alpha -= 255 // self.life_time  # 徐々に透明にする
        if self.alpha <= 0:
            self.kill()  # 透明になったら削除

    def draw(self, screen):
        """ 画面にアイテム画像とテキストを描画 """
        if not self.item_name == "points":
            if self.image:
                screen.blit(self.image, (self.rect_x, self.rect_y))
            screen.blit(self.text_image, (self.rect_x + 40, self.rect_y + 20))
        else: 
            screen.blit(self.text_image, (self.rect_x , self.rect_y))

#maingame処理

def spawn_Zombie(instance, kind):
    from Character import Zombie, FastZombie  # ここで遅延インポート

    enemy_classes = {
        "Zombie": Zombie,
        "FastZombie": FastZombie
    }

    current_time = instance.current_time
    last_spawn_time = getattr(instance, f"{kind}_last_spawn_time")
    spawn_interval = getattr(instance, f"{kind}_spawn_interval")

    # ここを修正
    enemy_type = enemy_classes.get(kind)  

    if enemy_type is None:
        raise ValueError(f"敵の種類 '{kind}' が見つかりません")

    if current_time - last_spawn_time > spawn_interval:
        zombie_new = enemy_type(screen_width, GRID_CENTER[0][random.randint(0, GRID_V_Number-2)][1], instance)
        instance.all_sprites.add(zombie_new)
        instance.zombies.add(zombie_new)
        setattr(instance, f"{kind}_last_spawn_time", current_time)  # スポーン時間を更新

def text_item(pos, item, limit, require, instance):
    if limit >= require:
        color = WHITE
    else:
        color = RED
    font_small = pygame.font.SysFont(None, 30)
    if item == "points":
        text = font_small.render("points", True, color)
        instance.screen.blit(text, pos)
    else:
        image = item_image_dict[item]
        instance.screen.blit(image, pos)
    pos_x, pos_y = pos
    text = font_small.render(f":{limit}/{require}", True, color)
    instance.screen.blit(text, (pos_x + 60, pos_y))    

def item_consume(plant_cost, plant_items, instance):
    # ポイントとアイテムのチェック  
        if plant_cost is not None:
            if instance.points < plant_cost:
                error_text = Error(instance.screen, "You don't have enough points")
                instance.texts.add(error_text)
                return False
            
            # アイテム不足をチェック
            for item, required_amount in plant_items.items():
                if instance.item.get(item, 0) < required_amount:
                    error_text = Error(instance.screen, f"You don't have enough {item}")
                    instance.texts.add(error_text)
                    return False
            
            # ポイントを減算
            instance.points -= plant_cost

            # アイテムを消費
            for item, required_amount in plant_items.items():
                instance.item[item] -= required_amount
            
            return True
            
Plant_cost = 10
StrongPlant_cost = 30
Rock_cost = 5
Obsidian_cost = 30
Fire_cost = 20 ; Fire_item = {"fire element": 2}
Water_cost = 15 ; Water_item = {"water element": 2}
Thunder_cost = 15 ; Thunder_item = {"thunder element": 2}
