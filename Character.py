import pygame
import random
from Back_Process import *


pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("简单的PvZ游戏")

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
        self.image = pygame.Surface((80, 80))  
        self.image.fill(GREEN)  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.peas = pygame.sprite.Group()  
        self.last_shot = instance.current_time
        self.name = "Plant"
        self.upper_plant = "StrongPlant"
        self.levelup_cost = 30
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

    def update(self):
        self.current_time = self.instance.current_time
        if self.current_time - self.last_shot > self.attack_interval:  
            self.shoot_pea()
            self.last_shot = self.current_time
        
        if self.hp <= 0:
            self.kill()

        self.peas.update()
    
    def draw_hp_bar(self, screen):
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

    def shoot_pea(self):
        pea = self.Pea(self.rect.x + self.rect.width, self.rect.y + 20)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    def show_levelup_text(self):
        self.LevelupButton(self, self.instance)
        self.noLevelupButton(self, self.instance)
        self.Leveluptext(self)
        
    class LevelupButton(pygame.sprite.Sprite):
        def __init__(self, plant, instance):
            super().__init__()
            self.rect = pygame.Rect(plant.rect.x , plant.rect.y -30, 30, 30)
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # 透明対応
            self.image.fill((0, 0, 0, 0))  # 完全透明にする
            self.plant = plant
            self.draw()

            self.screen = plant.screen
            self.instance = instance
            instance.buttons.add(self)
            plant.button_sprites.add(self)
            
        def draw(self):
            pygame.draw.rect(self.image, BLACK, (0,0, 40, 25), width=2)
            font = pygame.font.SysFont(None, 30)
            text = font.render("OK", True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            self.image.blit(text, (5,5))



        def Process(self):
            self.current_point = self.instance.points
            if self.current_point >= self.plant.levelup_cost:
                    self.upper_class = globals().get(self.plant.upper_plant)
                    self.new_plant = self.upper_class(self.plant.rect.x, self.plant.rect.y, self.instance)
                    self.plant.kill()
                    self.instance.all_sprites.add(self.new_plant)
                    self.instance.plants.add(self.new_plant)
                    self.instance.points -= self.plant.levelup_cost
                    for sprite in self.plant.button_sprites:
                        sprite.kill()
                        del sprite
            else:
                    self.new_error = Error(self.screen, "You don't have enough points!")
                    self.instance.errors.add(self.new_error)
        
        def update(self):
            if not self.plant.alive():  # 親が生存しているかチェック
                self.kill()  # 自分も削除
        

    class noLevelupButton(pygame.sprite.Sprite):
            def __init__(self, plant, instance):
                super().__init__()
                self.rect = pygame.Rect(plant.rect.x + 40, plant.rect.y -30, 30, 30)
                self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # 透明対応
                self.image.fill((0, 0, 0, 0))  # 完全透明にする
                self.draw()
                self.plant = plant
                self.screen = plant.screen
                self.instance = instance
                instance.buttons.add(self)
                plant.button_sprites.add(self)
            
            def draw(self):
                pygame.draw.rect(self.image, BLACK, (0, 0, 40, 25), width=2)
                font = pygame.font.SysFont(None, 30)
                text = font.render("NO!", True, BLACK)
                text_rect = text.get_rect(center=self.rect.center)
                self.image.blit(text, (5, 5))

            def Process(self):
                self.plant.leveluptext = False
                for sprite in self.plant.button_sprites:
                    sprite.kill()
                    del sprite

            def update(self):
                if not self.plant.alive():  # 親が生存しているかチェック
                    self.kill()  # 自分も削除
                    
    class Leveluptext(pygame.sprite.Sprite):
        def __init__(self, plant):
            super().__init__()
            self.rect = pygame.Rect(plant.rect.x, plant.rect.y - 50, 200, 30)  # メッセージ表示位置
            self.image = self.image = pygame.Surface((120, 50), pygame.SRCALPHA)  # 透明対応
            self.image.fill((0, 0, 0, 0))  # 完全透明にする
            self.draw()
            plant.button_sprites.add(self)
            plant.instance.buttons.add(self)
            self.plant= plant

        def draw(self):
            font = pygame.font.SysFont(None, 36)
            level_up_message = font.render("Level up?", True, BLACK)
            self.image.blit(level_up_message, (0, 5))

        def Process(self):
            pass

        def update(self):
            if not self.plant.alive():  # 親が生存しているかチェック
                self.kill()  # 自分も削除

    class Pea(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.name = "Pea"
            self.image = pygame.Surface((10, 5)) 
            self.image.fill(BROWN)  
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed = 5
            self.attack = 20

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
        self.image.fill(BLUE)
        self.max_hp = 200
        self.hp = self.max_hp

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
        self.name = "Rock"
        self.image = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))  
        self.image.fill(BROWN)  # Nutの色をブラウンに設定
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.upper_plant = "Obsidian"
        self.levelup_cost = 30
        self.leveluptext = False
        self.attack = 0
         # Nut植物はHPが高い（攻撃はしないがゾンビを止める）

        instance.nuts.add(self)
        instance.all_sprites.add(self)
        

        self.max_hp = 150  # 最大HP
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅

        self.button_sprites = pygame.sprite.Group()
        
class Thunder(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.image.fill((255, 255, 0))  # 黄色
        self.attack_power = 10  # ダメージ量
        self.cost = 15
        self.attack_interval = 1000  # 1秒ごとに攻撃
        self.last_attack_time = pygame.time.get_ticks()
        self.name = "Thunder"
        self.pea_type = ThunderPea  # 発射する弾の種類
        self.max_hp = 200
        self.hp = self.max_hp

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_interval:
            self.shoot_pea()
            self.last_attack_time = current_time

    def shoot_pea(self):
        pea = self.pea_type(self.rect.x + self.rect.width, self.rect.y + 20, self.instance)
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

class ThunderPea(Plant.Pea):
    def __init__(self, x, y, instance):
        super().__init__(x, y)
        self.image.fill((255, 255, 0))  # 雷の弾
        self.attack = 15
        self.instance = instance

    def update(self):
        self.rect.x += self.speed  # 弾を前進させる
        if self.rect.x > screen_width: 
            self.kill()

    def collide(self, zombie):
        zombie.hp -= self.attack
        if zombie.hp <= 0:
            zombie.kill()
        self.chain_attack(zombie)
        self.kill()

    def chain_attack(self, hit_enemy):
        for other_enemy in self.instance.zombies:
            if abs(other_enemy.rect.centerx - hit_enemy.rect.centerx) <= GRID_WIDTH and \
               abs(other_enemy.rect.centery - hit_enemy.rect.centery) <= GRID_HEIGHT:
                other_enemy.hp -= self.attack // 2  # 連鎖ダメージは半分
                if other_enemy.hp <= 0:
                    other_enemy.kill()


    def update(self):
        if self.hp <= 0:
            self.kill()

    def take_damage(self, damage, zombie):
        """Nutにダメージを与える"""
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
    
    def draw_hp_bar(self, screen):
        """HPバーをゾンビの上に描画"""
        self.screen = screen
        bar_x = self.rect.x
        bar_y = self.rect.y - 10  # ゾンビの上に配置
        hp_ratio = self.hp / self.max_hp  # HPの割合
        hp_width = int(self.hp_bar_width * hp_ratio)  # HPバーの現在の長さ
        
        # HPバーの枠（黒）
        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, self.hp_bar_width + 2, 6))
        # HPバーの本体（赤）
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_width, 4))

    def show_levelup_text(self):
        self.LevelupButton(self, self.instance)
        self.noLevelupButton(self, self.instance)
        self.Leveluptext(self)

    class LevelupButton(pygame.sprite.Sprite):
        def __init__(self, plant, instance):
            super().__init__()
            self.rect = pygame.Rect(plant.rect.x , plant.rect.y -30, 30, 30)
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # 透明対応
            self.image.fill((0, 0, 0, 0))  # 完全透明にする
            self.plant = plant
            self.draw()

            self.screen = plant.screen
            self.instance = instance
            instance.buttons.add(self)
            plant.button_sprites.add(self)
            
        def draw(self):
            pygame.draw.rect(self.image, BLACK, (0,0, 40, 25), width=2)
            font = pygame.font.SysFont(None, 30)
            text = font.render("OK", True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            self.image.blit(text, (5,5))



        def Process(self):
            self.current_point = self.instance.points
            if self.current_point >= self.plant.levelup_cost:
                    self.upper_class = globals().get(self.plant.upper_plant)
                    self.new_plant = self.upper_class(self.plant.rect.x, self.plant.rect.y, self.instance)
                    self.plant.kill()
                    self.instance.all_sprites.add(self.new_plant)
                    self.instance.nuts.add(self.new_plant)
                    self.instance.points -= self.plant.levelup_cost
                    for sprite in self.plant.button_sprites:
                        sprite.kill()
                        del sprite
            else:
                    self.new_error = Error(self.screen, "You don't have enough points!")
                    self.instance.errors.add(self.new_error)

        def update(self):
            if not self.plant.alive():  # 親が生存しているかチェック
                self.kill()  # 自分も削除
        

    class noLevelupButton(pygame.sprite.Sprite):
            def __init__(self, plant, instance):
                super().__init__()
                self.rect = pygame.Rect(plant.rect.x + 40, plant.rect.y -30, 30, 30)
                self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # 透明対応
                self.image.fill((0, 0, 0, 0))  # 完全透明にする
                self.draw()
                self.plant = plant
                self.screen = plant.screen
                self.instance = instance
                instance.buttons.add(self)
                plant.button_sprites.add(self)
            
            def draw(self):
                pygame.draw.rect(self.image, BLACK, (0, 0, 40, 25), width=2)
                font = pygame.font.SysFont(None, 30)
                text = font.render("NO!", True, BLACK)
                text_rect = text.get_rect(center=self.rect.center)
                self.image.blit(text, (5, 5))

            def Process(self):
                self.plant.leveluptext = False
                for sprite in self.plant.button_sprites:
                    sprite.kill()
                    del sprite

            def update(self):
                if not self.plant.alive():  # 親が生存しているかチェック
                    self.kill()  # 自分も削除
                    
    class Leveluptext(pygame.sprite.Sprite):
        def __init__(self, plant):
            super().__init__()
            self.rect = pygame.Rect(plant.rect.x, plant.rect.y - 50, 200, 30)  # メッセージ表示位置
            self.image = self.image = pygame.Surface((120, 50), pygame.SRCALPHA)  # 透明対応
            self.image.fill((0, 0, 0, 0))  # 完全透明にする
            self.draw()
            plant.button_sprites.add(self)
            plant.instance.buttons.add(self)
            self.plant = plant

        def draw(self):
            font = pygame.font.SysFont(None, 36)
            level_up_message = font.render("Level up?", True, BLACK)
            self.image.blit(level_up_message, (0, 5))

        def Process(self):
            pass
        
        def update(self):
            if not self.plant.alive():  # 親が生存しているかチェック
                self.kill()  # 自分も削除


class Obsidian(Rock):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.image.fill((50, 40, 30))
        self.max_hp = 400
        self.hp = self.max_hp
        self.attack = 40

    def take_damage(self, damage, zombie):
        """Nutにダメージを与える"""
        self.hp -= damage
        zombie.hp -= self.attack
        if self.hp <= 0:
            self.kill()

class Fire(Plant):
    def __init__(self, x, y, instance):
        super().__init__(x, y, instance)
        self.image.fill(ORANGE)
        self.name = "Fire"
        self.levelup_cost = 60
        self.cost = 20
        self.upper_plant = "StrongFire"
        self.instance = instance

    def shoot_pea(self):
        pea = self.FirePea(self.rect.x + self.rect.width, self.rect.y + 20, self)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    class FirePea(Plant.Pea):
        def __init__(self, x, y, plant):
            super().__init__(x, y)
            self.image.fill(BROWN)
            self.plant = plant
            self.attack = 10

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
                self.image = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
                self.spawn = pygame.time.get_ticks()
                self.interval = 5000
                self.attack = 5
                self.rect = self.image.get_rect()
                self.rect.topleft = pos
                self.draw()
                
            def draw(self):
                pygame.draw.rect(self.image, ORANGE, (0, 0, self.rect.width, self.rect.height), width=5)

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
        self.image.fill(LIGHTBLUE)
        self.name = "Water"
        self.levelup_cost = 50
        self.cost = 15
        self.upper_plant = "StrongWater"
        self.instance = instance
        self.attack_interval = 2000
        

    def shoot_pea(self):
        pea = self.WaterPea(self.rect.x + self.rect.width, self.rect.y + 20, self)  
        self.peas.add(pea)
        self.instance.all_sprites.add(pea)

    class WaterPea(Plant.Pea):
        def __init__(self, x, y, plant):
            super().__init__(x, y)
            self.image = pygame.Surface((100, 5))
            self.image.fill(LIGHTBLUE)
            self.plant = plant
            self.attack = 30
            self.attacked_zombies = set()  # 攻撃済みのゾンビを記録
            self.lifetime = 200
            self.speed = 5

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

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, instance):
        super().__init__()
        self.instance = instance
        self.level = instance.current_level
        self.name = "Zombie"
        self.image = pygame.Surface((80, 80)) 
        self.image.fill(RED)  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1
        self.attack_interval = 1000
        self.attack = 35 + 10 * (self.level -1)
        

        self.max_hp = 100 + 40 * (self.level -1) # 最大HP
        self.hp = self.max_hp  # 現在のHP
        self.hp_bar_width = 80  # HPバーの横幅

        self.font = pygame.font.Font(None, 24)  
        self.message_text = ""  # メッセージ用の変数

        self.collide = False
        self.collide_Nut = None
        self.last_attack_time = {}  # 各プラントごとの攻撃時間を記録

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

    def draw_hp_bar(self, screen):
        """HPバーをゾンビの上に描画"""
        bar_x = self.rect.x
        bar_y = self.rect.y - 10  # ゾンビの上に配置
        hp_ratio = self.hp / self.max_hp  # HPの割合
        hp_width = int(self.hp_bar_width * hp_ratio)  # HPバーの現在の長さ
        
        # HPバーの枠（黒）
        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, self.hp_bar_width + 2, 6))
        # HPバーの本体（赤）
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, hp_width, 4))
        self.level_text = self.instance.font.render(f"level{self.level}", True, RED)
        screen.blit(self.level_text, (bar_x, bar_y - 20))

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
        self.image = pygame.Surface((20, 20)) 
        self.image.fill(pygame.Color("yellow"))  
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height  
        self.speed = 1  

    def update(self):
        self.rect.y += self.speed  
        if self.rect.y > screen_height:  
            self.kill()
            del self