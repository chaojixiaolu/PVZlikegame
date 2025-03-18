import pygame
import random


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
    
    def draw(self):
        """ メッセージを画面に描画 """
        self.screen.blit(self.text_message, self.rect)

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
        self.cost = getattr(self.instance, f"{self.mode}_cost", None)
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
