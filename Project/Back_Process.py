import pygame
import random
import os

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

def load_animation_frames(instance): # アニメーションフレームを読み込む
    if instance.animation:    
        for i in range(instance.frames):  
            img_path = f"{instance.path}_{i:05}.png"
            if os.path.exists(img_path):
                frame = pygame.image.load(img_path)
                if i == 0:
                    instance.art_rect = frame.get_rect()
                    instance.art_dif_x = (instance.art_rect.width - instance.rect.width)/2
                    instance.art_dif_y = (instance.art_rect.height - instance.rect.height)/2
                instance.animation_frames.append(frame)
            else:
                print(f"Warning: {img_path} not found")
    else:
        img_path = f"{instance.path}.png"
        instance.art = pygame.image.load(img_path)
        instance.art_rect = instance.art.get_rect()
        instance.art_dif_x = (instance.art_rect.width - instance.rect.width)/2
        instance.art_dif_y = (instance.art_rect.height - instance.rect.height)/2

def load_attack_animation_frames(instance):
    if instance.attack_animation:
        for j in range(instance.attack_frames + 1):
            img_path = f"{instance.attack_path}_{j:05}.png"
            if os.path.exists(img_path):
                frame = pygame.image.load(img_path)
                instance.attack_animation_frames.append(frame)    
            else:
                print(f"Warning: {img_path} not found")
    else:
        pass

def drawattack(screen, instance):
    if not hasattr(instance, "is_attacking"):  # instanceがis_attackingを持っていない場合はスキップ
        return
    
    if instance.attack_animation:
        """攻撃アニメーションを再生する"""
        if instance.is_attacking:
            target = instance.is_attacking
            if instance.attack_frame_count < instance.attack_frames:
                attack_frame = instance.attack_animation_frames[instance.attack_frame_count]
                screen.blit(attack_frame, (target.rect.x - 60, target.rect.y - 60))
                instance.attack_frame_count += 1
            else:
                instance.attack_frame_count = 0
                instance.is_attacking = False  # 攻撃終了

def drawart(screen, instance):
    if instance.animation:
        # アニメーションを描画
        if instance.animation_frames:
            frame = instance.animation_frames[instance.frame_count]  # 現在のフレームを選択
            screen.blit(frame, (instance.rect.x - instance.art_dif_x, instance.rect.y - instance.art_dif_y))  # アニメーションフレームを描画
        else:
            print("No animation frames to draw!")
        instance.frame_count = (instance.frame_count + 1) % instance.frames
    else:
        screen.blit(instance.image, instance.rect)
        screen.blit(instance.art, (instance.rect.x - instance.art_dif_x, instance.rect.y - instance.art_dif_y))

#Character処理

class DropItemText(pygame.sprite.Sprite):
    def __init__(self, item_name, number,  pos, instance):
        super().__init__()
        self.instance = instance
        self.item_name = item_name  # ドロップしたアイテムの名前
        self.rect_x,  self.rect_y = pos
        self.alpha = 255  # 透明度
        self.life_time = 60  # 60フレーム（1秒）で消える
        self.image = item_image_dict.get(f"{item_name}_image", None)  # アイテムの画像

        self.font = pygame.font.Font(None, 24)
        self.text_image = self.font.render(f"x{number}", True, (255, 255, 255))  # "×1" のテキスト

    def update(self):
        """ アイテムを上に浮かせ、徐々に透明にする """
        self.rect_y -= 1  # 1フレームごとに上へ移動
        self.alpha -= 255 // self.life_time  # 徐々に透明にする
        if self.alpha <= 0:
            self.kill()  # 透明になったら削除

    def draw(self, screen):
        """ 画面にアイテム画像とテキストを描画 """
        if self.image:
            image_copy = self.image.copy()
            image_copy.set_alpha(self.alpha)  # 透明度を設定
            screen.blit(image_copy, (self.rect_x, self.rect_y))
        screen.blit(self.text_image, (self.rect_x + 40, self.rect_y + 20))

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

item_image_dict = \
    {"fire element_image": pygame.image.load("Assets/fire element.png"),  \
    "water element_image": pygame.image.load("Assets/water element.png"),  \
    "thunder element_image": pygame.image.load("Assets/thunder element.png")}

Plant_cost = 10
Rock_cost = 5
Fire_cost = 20 ; Fire_item = {"fire element": 2}
Water_cost = 15 ; Water_item = {"water element": 2}
Thunder_cost = 15 ; Thunder_item = {"thunder element": 2}
