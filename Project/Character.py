import pygame
import random
from Back_Process import *
import math
from Load_data import *

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Elemental Diffence")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)  
RED = (255, 0, 0) 
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHTBLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
LIGHTRED = (255, 150 ,150)
DEEPOBS = (40, 36, 36)


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

class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, instance):
        super().__init__()
        self.instance = instance
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)  # 透過サーフェス
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.peas = pygame.sprite.Group()
        self.last_shot = instance.current_time
        self.name = "Plant"
        self.upper_plant = "StrongPlant"
        self.color = WHITE
        self.cost = 10
        self.attack_interval = 1000


        self.max_hp = 100  # 最大HP
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅

        self.leveluptext = False
        self.circle_button_rect = pygame.Rect(self.rect.x +10, self.rect.y -30, 30, 30)
        self.cross_button_rect = pygame.Rect(self.rect.x + 40, self.rect.y - 30, 30, 30)
        
        self.button_sprites = pygame.sprite.Group()

        instance.all_sprites.add(self)
        instance.plants.add(self)

        self.animation = False
        self.attack_animation = False
        self.art_count = 0
        self.attack_count = 0
       
    def update(self):
        self.current_time = self.instance.current_time
        if self.current_time - self.last_shot > self.attack_interval:  
            self.shoot_pea()
            self.last_shot = self.current_time
        
        if self.hp <= 0:
            self.kill()

        self.peas.update()

    def shoot_pea(self):
        pea = self.Pea(self.rect.x + self.rect.width, self.rect.y + 20)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    def clicked(self):
        self.instance.start_zoom_in(self, "levelup")

    class Pea(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.name = "Pea"
            self.image = pygame.Surface((10, 5), pygame.SRCALPHA) 
            self.art = pygame.image.load("Assets/Pea.png")  
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed = 5
            self.attack = 20
            
            self.animation = False
            self.attack_animation = False
            self.art_count = 0
            self.attack_count = 0

        def draw_hp(self, screen):
            pass

        def update(self):
            self.rect.x += self.speed  
            if self.rect.x > screen_width: 
                self.kill()
                del self

        def collide(self, zombie):
            zombie.hp -= self.attack
            self.kill()
            del self

class StrongPlant(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "StrongPlant"
        self.max_hp = 200
        self.hp = self.max_hp

        
        self.animation = True
        self.attack_animation = False
        self.art_count = 0
        self.attack_count = 0
        
    def draw_hp(self, screen):
        """HPバーをプラントの上に描画"""
        bar_x = self.rect.x
        bar_y = self.rect.y - 10  # ゾンビの上に配置
        hp_ratio = self.hp / self.max_hp  # HPの割合
        hp_width = int(self.hp_bar_width * hp_ratio)  # HPバーの現在の長さ
        self.screen = screen

        # HPバーの枠（黒）
        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, self.hp_bar_width + 2, 6))
        # HPバーの本体（緑）
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_width, 4))

    class BluePea(Plant.Pea):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.image.fill(BLUE)  # 青色の Pea
            self.name = "BluePea"
            self.attack = 50

    def shoot_pea(self):
        blue_pea = self.BluePea(self.rect.x + self.rect.width, self.rect.y + 20)
        self.peas.add(blue_pea)
        self.instance.all_sprites.add(blue_pea)
       
class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y, instance):
        super().__init__()
        self.instance = instance
        self.screen = instance.screen
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = "Rock"
        self.upper_plant = "Obsidian"
        self.color = YELLOW
        self.levelup_cost = 30
        self.leveluptext = False
        self.attack = 0
        self.stop_zombie = True
         # Nut植物はHPが高い（攻撃はしないがゾンビを止める）

        
        instance.plants.add(self)
        instance.all_sprites.add(self)
        
        self.max_hp = 200  # 最大HP
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅

        self.button_sprites = pygame.sprite.Group()

        
        self.animation = False
        self.attack_animation = False
        self.art_count = 0
        self.attack_count = 0

    def update(self):
        if self.hp <= 0:
            self.kill()

    def take_damage(self, damage, zombie):
        """Nutにダメージを与える"""
        self.hp -= damage
        if self.hp <= 0:
            self.kill()

    def clicked(self):
        self.insatnce.start_zoom_in(self, "levelup")
   
class Obsidian(Rock):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "Obsidian"
        self.color = DEEPOBS

        self.max_hp = 600
        self.hp = self.max_hp
        self.attack = 40
        
        self.is_attacking = False  # 攻撃中フラグ
        self.animation = True
        self.attack_animation = True
        self.art_count = 0
        self.attack_count = 0
        
    def take_damage(self, damage, zombie):
        """Nutにダメージを与える"""
        self.hp -= damage
        zombie.hp -= self.attack
        self.is_attacking = zombie
        if self.hp <= 0:
            self.kill()
    
    def update(self):
        if self.is_attacking and not self.is_attacking.alive():
            self.is_attacking = False
        if self.hp <= 0:
            self.kill()
       
    def clicked(self):
        self.leveluptext = True

class Fire(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)  # 透過サーフェス
        self.name = "Fire"
        self.levelup_cost = 60
        self.cost = 20
        self.upper_plant = "StrongFire"
        self.instance = instance

        self.animation = True
        self.attack_animation = False
        self.art_count = 0
        self.attack_count = 0

    def shoot_pea(self):
        pea = self.FirePea(self.rect.x + self.rect.width, self.rect.y + 20, self)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    class FirePea(Plant.Pea):
        def __init__(self, x, y, plant):
            super().__init__(x, y)
            self.name = "FirePea"
            self.plant = plant
            self.attack = 10
            
            self.animation = True
            self.art_count = 0
            self.attack_count = 0

        def collide(self, zombie):
            self.collide_pos = get_grid_center(zombie.rect.x, zombie.rect.y)
            if self.collide_pos:  # グリッドが取得できたら
                self.new_trap = Fire.FirePea.Fire_trap(self.collide_pos, self.plant)
                self.plant.instance.traps.add(self.new_trap)
                zombie.hp -= self.attack
            self.kill()
            del self

        class Fire_trap(pygame.sprite.Sprite):
            def __init__(self, pos, plant):
                super().__init__()
                self.name = "FireTrap"
                self.image = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
                self.spawn = pygame.time.get_ticks()
                self.interval = 5000
                self.attack = 5
                self.rect = self.image.get_rect()
                self.rect.topleft = pos

                self.animation = True
                self.attack_animation = False
                self.art_count = 0
                self.attack_count = 0

            def collide(self, zombie):
                self.current_time = pygame.time.get_ticks()
                if self.current_time % 1000 < 50:
                    zombie.hp -= self.attack
                
            def update(self):
                self.current_time = pygame.time.get_ticks()
                if self.current_time - self.spawn > self.interval:
                    self.kill()
                    del self

class Water(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "Water"
        self.levelup_cost = 50
        self.cost = 15
        self.upper_plant = "StrongWater"
        self.instance = instance
        self.attack_interval = 2000

        self.animation = True

    def shoot_pea(self):
        pea = self.WaterPea(self.rect.x + self.rect.width, self.rect.y + 20, self)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    class WaterPea(Plant.Pea):
        def __init__(self, x, y, plant):
            super().__init__(x, y)
            self.name = "WaterPea"
            self.image = pygame.Surface((100, 5), pygame.SRCALPHA)
            self.plant = plant
            self.attack = 30
            self.attacked_zombies = set()  # 攻撃済みのゾンビを記録
            self.lifetime = 200
            self.speed = 5

            self.animation = True

        def update(self):
            self.rect.x += self.speed  # 右に移動
            self.lifetime -= 1  # 寿命を減らす
            if self.lifetime <= 0 or self.rect.x > screen_width:
                self.kill()  # 時間経過または画面外で削除
                del self

        def collide(self, zombie):
            if zombie not in self.attacked_zombies:  # まだ攻撃していないゾンビなら
                zombie.hp -= self.attack
                self.attacked_zombies.add(zombie)  # 攻撃済みに追加

class Thunder(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.attack_power = 30  # ダメージ量
        self.cost = 15
        self.attack_interval = 2500  # 1秒ごとに攻撃
        self.last_attack_time = pygame.time.get_ticks()
        self.name = "Thunder"

        self.animation = True

    def shoot_pea(self):
        pea = self.ThunderPea(self.rect.x + self.rect.width, self.rect.y + 20, self)
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    class ThunderPea(Plant.Pea):
        def __init__(self, x, y, plant):
            super().__init__(x, y)
            self.name = "ThunderPea"
            self.image.fill((255, 255, 0))  # 雷の弾
            self.attack = 25
            self.plant = plant
            self.instance = plant.instance
            self.hit_zombies = set()  # すでに当たったゾンビを記録するセット

            self.animation = True


        def update(self):
            self.rect.x += self.speed  # 弾を前進させる
            if self.rect.x > screen_width: 
                self.kill()

        def collide(self, zombie):
            zombie.hp -= self.attack
            self.hit_zombies.add(zombie)  # このゾンビは二度当たらないようにする
            if zombie.hp <= 0:
                zombie.kill()
            else:
                self.chain_attack(zombie)
            self.kill()

        def chain_attack(self, hit_enemy):
            """近くのゾンビを探して雷を飛ばし、連鎖攻撃する"""
            chain_range = 200  # 200px以内のゾンビを対象
            possible_targets = []

            # 近くのゾンビを探す
            for other_enemy in self.instance.all_sprites:
                if isinstance(other_enemy, Zombie) and other_enemy not in self.hit_zombies:
                    distance = math.sqrt((other_enemy.rect.centerx - hit_enemy.rect.centerx) ** 2 + 
                                        (other_enemy.rect.centery - hit_enemy.rect.centery) ** 2)
                    if distance <= chain_range:
                        possible_targets.append(other_enemy)

            if possible_targets:
                next_target = random.choice(possible_targets)  # ランダムに1体選ぶ
                self.draw_lightning(hit_enemy, next_target)  # 雷の線を描画
                next_target.hp -= self.attack // 2  # ダメージを半分にする
                self.hit_zombies.add(next_target)  # このゾンビを当たったリストに追加

                if next_target.hp <= 0:
                    next_target.kill()
                else:
                    self.chain_attack(next_target)  # さらに連鎖攻撃

        def draw_lightning(self, start_enemy, end_enemy):
            """ゾンビ間に黄色い線（雷）を描画"""
            pygame.draw.line(self.instance.screen, (255, 255, 0), 
                            (start_enemy.rect.centerx, start_enemy.rect.centery), 
                            (end_enemy.rect.centerx, end_enemy.rect.centery), 3)

#敵

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, instance):
        super().__init__()
        self.instance = instance
        self.level = instance.current_level
        self.name = "Zombie"
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)   
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1
        self.attack_interval = 1000
        self.attack = 35 + 10 * (self.level -1)
        self.points = 10
        
        self.max_hp = 100 + 40 * (self.level -1) # 最大HP
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅

        self.font = pygame.font.Font(None, 24)  
        self.message_text = ""  # メッセージ用の変数

        self.collide = False
        self.collide_Nut = None
        self.last_attack_time = {}  # 各プラントごとの攻撃時間を記録

        self.is_attacking = False

        self.animation = False
        self.attack_animation = True
        self.art_count = 0
        self.attack_count = 0
    
    def collide_stop(self, collide_Nut):
        """ ゾンビをナッツの手前で止める """
        if not self.collide:
            self.collide = True
            self.collide_Nut = collide_Nut
            self.Position = collide_Nut.rect.x + GRID_WIDTH
            self.collide_Nut.take_damage(self.attack, self)  # ナッツに接触した瞬間に攻撃を開始する
            self.last_attack_time[self.collide_Nut] = self.instance.current_time
 
    def update(self):
        """ ゾンビの移動と攻撃処理 """
        if self.collide:
            if self.collide_Nut is None or self.collide_Nut.alive() == False:
                self.collide = False
                self.collide_Nut = None
            else:    
                self.rect.x = self.Position  # ナッツの手前で停止
                self.damage_to_plant(self.collide_Nut)  # ナッツにダメージを与える
        else:
            self.rect.x -= self.speed  # 通常移動

        if self.rect.x < 0:
            self.instance.deadcount += 1
            self.kill()
            del self
        
    def message(self, screen):
        """ ゾンビの上にテキストを表示する """
        if self.message_text:
            text_image = self.font.render(self.message_text, True, BLACK)  
            screen.blit(text_image, (self.rect.x, self.rect.y - 25))  

    def damage_to_plant(self, target):
        """ プラントやナッツに攻撃可能 """
        self.current_time = self.instance.current_time
        # 初回攻撃の記録を作成
        
        if target not in self.last_attack_time:
            self.last_attack_time[target] = self.instance.current_time

        # `attack_interval` ごとにダメージを与える
        if self.current_time - self.last_attack_time[target] >= self.attack_interval:
            if isinstance(target, Plant):  # プラントの場合
                target.hp -= self.attack
            elif isinstance(target, Rock) or isinstance(target, Obsidian):  # ナッツの場合
                target.hp -= self.attack # ナッツへのダメージ
                self.hp -= target.attack
            self.last_attack_time[target] = self.current_time  # 次の攻撃時間を更新
    
    def drop_item(self):
        self.instance.points += self.points
        self.drop_dict = {}
        self.drop_rand = random.randint(1, 100)
        if self.drop_rand <= 25:
            self.drop_dict["fire element"] = 1
        elif self.drop_rand <= 50:
            self.drop_dict["water element"] = 1
        elif self.drop_rand <= 75:
            self.drop_dict["thunder element"] = 1
        
        i = 0
        drop_item_text = DropItemText("points", self.points, (self.rect.x, self.rect.y+5), self.instance)
        self.instance.texts.add(drop_item_text)
        for key, value in self.drop_dict.items(): #辞書にアイテムを追加
            self.instance.item[key] = self.instance.item.get(key, 0) + value
            drop_item_text = DropItemText(key, value, (self.rect.x, self.rect.y - (30 + i * 20)), self.instance)
            self.instance.texts.add(drop_item_text)
            i += 1

class FastZombie(Zombie):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.image.fill(LIGHTRED)
        self.speed = 8
        self.attack_interval = 500

class YellowItem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.name = "YellowItem"
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA) 
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height  
        self.speed = 1  

        self.animation = True
        self.attack_animation = False
        self.art_count = 0
        self.attack_count = 0
        
    def update(self):
        self.rect.y += self.speed  
        if self.rect.y > screen_height:  
            self.kill()
            del self

class TotemInit(pygame.sprite.Sprite):
    def __init__(self, x, y, instance):
        super().__init__()
        self.color = WHITE
        self.instance = instance
        self.name = "TotemInit"
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)  # 透過サーフェス
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.product = None
        self.value = 1

        self.max_hp = 100
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅


        self.process_rate = 0
        self.last_produce_time = 0
        self.process_time = 5000
        self.process_bar_width = 80

        self.instance.all_sprites.add(self)
        self.instance.plants.add(self)

        self.animation = False
        self.attack_animation = False
        self.art_count = 0
        
    def clicked(self):
        self.instance.start_zoom_in(self, "Totem")

    def update(self):
        self.drop_dict = {self.product: self.value}
        self.process_rate = (self.instance.current_time - self.last_produce_time) * 100 / self.process_time
        self.draw_process_bar()
        if self.process_rate >= 100:
            self.produce()
            self.last_produce_time = self.instance.current_time
            self.process_rate = 0
    
    def draw_process_bar(self):
        if self.product:
            bar_x = self.rect.x
            bar_y = self.rect.y - 5  #トーテムの上に配置
            process_width = int(self.process_bar_width * self.process_rate / 100)  # HPバーの現在の長さ
        
            # HPバーの枠（黒）
            pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, self.process_bar_width + 2, 6))
            # HPバーの本体（黄）
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, process_width, 4))

    def produce(self):
        if self.product:
            i = 0
            for key, value in self.drop_dict.items(): #辞書にアイテムを追加
                self.instance.item[key] = self.instance.item.get(key, 0) + value
                drop_item_text = DropItemText(key, value, (self.rect.x, self.rect.y - (30 + i * 20)), self.instance)
                self.instance.texts.add(drop_item_text)
                i += 1
        
class TotemFire(TotemInit):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "TotemFire"
        self.product = "fire element"
        
        self.animation = True
        
class TotemWater(TotemInit):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "TotemWater"
        self.product = "water element"

        self.animation = True
        
class TotemThunder(TotemInit):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.name = "TotemThunder"
        self.product = "thunder element"

        self.animation = True
       