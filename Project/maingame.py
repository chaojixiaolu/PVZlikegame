import pygame
import random
from Character import * 
from Back_Process import *
import objgraph
import gc
import graphviz
from Load_data import *



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


# グリッド設定
GRID_HEIGHT = 80
GRID_WIDTH = 80
GRID_V_Number = 4
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



class maingame():
    def game_loop(self):
        clock = pygame.time.Clock()
        running = True
        self.paused = False 
        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 30)
        self.start_time = pygame.time.get_ticks()
        self.screen = screen

        self.Zombie_last_spawn_time = 0
        self.FastZombie_last_spawn_time = 0
        self.selected_plant = "Plant"  # デフォルトの選択植物はPea
        self.deadline = 5
        self.deadcount = 0
        self.current_level = 1  # 初期レベル
        self.current_time = 0
        self.level_up_time = 20000  # 3秒ごとにレベルアップ (ミリ秒単位)
        self.last_levelup = pygame.time.get_ticks()  # 最後にレベルアップした時間を記録

        self.pause_start_time = 0
        self.zoom_start_time = 0
        self.paused_duration = 0
        self.zoom_duration = 0

        self.zooming = False
        self.zooming_in = False
        self.zooming_out = False
        self.zoom_factor = 1.0
        self.zoom_target = 2.0  # 2倍ズーム
        self.zoom_to = None

        self.points = 50

        self.item = {"fire element": 0, "water element": 0, "thunder element": 0}

        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.plants = pygame.sprite.Group()
        self.yellow_items = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.texts = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.zoom_buttons = pygame.sprite.Group()

        self.plant = Plant(GRID_CENTER[2][1][0], GRID_CENTER[2][1][1], self)
        self.all_sprites.add(self.plant)
        self.plants.add(self.plant)

        self.zombie = Zombie(screen_width, GRID_CENTER[0][random.randint(0, GRID_V_Number-1)][1], self)
        self.all_sprites.add(self.zombie)
        self.zombies.add(self.zombie)

        back_image = pygame.image.load("Assets/Back.png")
        self.background = pygame.image.load("Assets/BackGround1.png").convert()
        self.arrow_image = pygame.image.load("Assets/Arrow.png")

        screen.blit(self.background, (0,0))
        Plantbutton(self)
        Rockbutton(self)
        PauseButton(self)
        Firebutton(self)
        Waterbutton(self)
        Thunderbutton(self)
        
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.current_time = pygame.time.get_ticks() - self.paused_duration - self.zoom_duration

             # **ゲームオーバーならループを抜ける**
            if self.deadcount > self.deadline:
                running = False
                break  # メインループを抜ける

            # **一時停止処理**
            if self.paused:
                self.pause_screen()

            #ズーム処理
            if self.zooming:
                self.zoom_screen()

            """時間経過でレベルアップ"""
            if self.current_time - self.last_levelup >= self.level_up_time:
                self.current_level += 1
                self.last_levelup = self.current_time  # 時間を更新
                
            self.sprite_positions = {}

            for sprite in self.all_sprites:
            # スプライトの名前と位置を辞書に保存
                self.sprite_positions[(sprite.rect.x, sprite.rect.y)] = sprite.name


            for event in pygame.event.get():  # イベントループ
                # print(f"Event detected: {event}")  # すべてのイベントを出力
                if event:
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        
                        if event.button == 1:  # 左クリック
                            mouse_grid = get_grid_center(mouse_x, mouse_y)
                            self.plant_added = False
                            self.button_pressed = False  # ボタンが押されたかどうかのフラグ

                            # ボタンの処理
                            for button in self.buttons:
                                if button.rect.collidepoint(event.pos):
                                    button.Process()
                                    self.button_pressed = True
                                    break  # クリック処理をボタンで完了するためにループを抜ける

                            if not self.button_pressed:
                                
                                # mouse_gridがNoneでない場合、またはgridの位置が設定されている場合に実行
                                if mouse_grid is not None:
                                    for plant in self.plants:
                                        # マウスクリックがプラントに当たった場合
                                        if plant.rect.collidepoint(event.pos):
                                            plant.clicked()
                                            self.start_zoom_in(plant)
                                            break  # それ以上の処理を避ける

                                        # もしクリックした位置に既存のプラントがない場合
                                    if self.sprite_positions.get(mouse_grid) is None and not self.plant_added:
                                        self.add_plant(mouse_grid[0], mouse_grid[1])

                                else:
                                    break  # mouse_gridがNoneの場合は何もしない

                        if event.button == 3:  # 右クリック
                            for item in self.yellow_items:
                                if item.rect.colliderect(pygame.Rect(mouse_x, mouse_y, 1, 1)):
                                    self.points += 5  # アイテムを集めたらポイントが増える
                                    item.kill()

            events = pygame.event.get()
            if len(events) > 50:  # 100以上のイベントが溜まっていたらリセット
                pygame.event.clear()


            if random.random() < 0.02:  # イエローアイテムスポーン
                new_item = YellowItem()
                self.all_sprites.add(new_item)
                self.yellow_items.add(new_item)

            
            self.Zombie_spawn_interval = random.randint(3000, 5000) #ゾンビのスポーン
            self.FastZombie_spawn_interval = random.randint(6000, 8000)
            spawn_Zombie(self, "Zombie")
            if self.current_level > 5:
                spawn_Zombie(self, "FastZombie")

            zombies_to_remove = [zombie for zombie in self.zombies if zombie.hp <= 0]
            for zombie in zombies_to_remove:
                    self.zombies.remove(zombie)
                    zombie.drop_item()
                    zombie.kill()  # ここで kill() を呼び出す
                    del zombie

            screen.blit(back_image, (-350,-450))
            screen.blit(self.background, (0,0))
            # screen.fill(BLACK)
            # bg_surface = draw_background()
            # screen.blit(bg_surface, (0, 0))

            # draw系

            for trap in self.traps:
                trap.art_count = drawart(screen, trap.animation, trap.rect.topleft, trap.name, trap.art_count)
            self.all_sprites.draw(screen)

            for plant in self.all_sprites:  #絵を描写
                plant.art_count = drawart(screen, plant.animation, plant.rect.topleft, plant.name, plant.art_count)
            
            for plant in self.plants: #HP
                draw_hp(screen, plant, GREEN)
            for zombie in self.zombies:
                draw_hp(screen, zombie, RED)
                draw_level(screen, zombie, RED)
            
            # スコア表示
            score_text = self.font.render(f"Points: {self.points}", True, WHITE)
            screen.blit(score_text, (10, 120))
            
            # モード表示
            mode_text = self.font.render(f"Mode: {self.selected_plant}", True, WHITE)
            screen.blit(mode_text, (screen_width - 200, screen_height - 40))

            # **時間の表示**
            elapsed_time = (self.current_time - self.start_time) // 1000  # ミリ秒 → 秒
            time_text = self.font.render(f"Time: {elapsed_time} s", True, WHITE)  # 黒色
            screen.blit(time_text, (screen_width - 150, 120))  # 右上に表示

            # カウント表示
            count_text = self.font.render(f"{self.deadcount}/{self.deadline}", True, RED)
            screen.blit(count_text, (10, 150))

            """現在のレベルを表示"""
            level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
            screen.blit(level_text, (10, screen_height -50 ))

            #アイテム表示
            i = 0
            for item, value in self.item.items():
                if item:
                    item_image_path = item_image_dict.get(item + "_image")
                    screen.blit(item_image_path, (120 + i * 60, 510))
                    item_text = self.font.render(f"×{value}", True, WHITE)
                    screen.blit(item_text, (160 + i * 60, 530))
                    i += 1

            for zombie in self.zombies:
                zombie.message(screen)
                if zombie.collide and zombie.collide_Nut and not zombie.collide_Nut.alive():
                    zombie.collide = False  # ナッツが消えたら再び移動
                    zombie.collide_Nut = None
                if zombie.is_attacking and not zombie.is_attacking.alive():
                    zombie.is_attacking = False
                if zombie.is_attacking:
                    attack_name = f"{zombie.name}Attack"
                    zombie.attack_count = drawart(screen, zombie.attack_animation, zombie.is_attacking.rect.topleft, attack_name, zombie.attack_count)
            
            for plant in self.plants:
                if hasattr(plant, "is_attacking"):
                    if plant.is_attacking:
                        attack_name = f"{plant.name}Attack"
                        plant.attack_count = drawart(screen, plant.attack_animation, plant.is_attacking.rect.topleft, attack_name, plant.attack_count)

            self.buttons.draw(screen)
            self.buttons.update()
            self.traps.draw(screen)
            for text in self.texts:
                text.draw(screen)

            self.traps.update()
            self.all_sprites.update()
            self.texts.update()

            for plant in self.plants:  # 衝突処理(タネ、ゾンビ)
                if hasattr(plant, "shoot_pea"):
                    for pea in plant.peas:  # タネとゾンビ衝突
                        collided_zombie = pygame.sprite.spritecollideany(pea, self.zombies)
                        if collided_zombie:
                            pea.collide(collided_zombie)

            for plant in self.plants:  # 衝突処理(プラント, ゾンビ)
                collided_zombie = pygame.sprite.spritecollideany(plant, self.zombies)
                if collided_zombie:
                    if hasattr(plant, "stop_zombie"):
                        collided_zombie.collide_stop(plant)
                    else:
                        collided_zombie.damage_to_plant(plant)
                    collided_zombie.is_attacking = plant

            for trap in self.traps:  # トラッぷとゾンビ衝突
                    collided_zombie = pygame.sprite.spritecollideany(trap, self.zombies)
                    if collided_zombie:
                        trap.collide(collided_zombie)
             
            pygame.display.flip()

            clock.tick(30)
            gc.collect()  # ガーベジコレクションを手動で実行
            # objgraph.show_growth()
            
        self.game_over_screen()  # ゲームオーバー画面を表示
    
    def add_plant(self, pos_x, pos_y):
        plant_class = globals().get(self.selected_plant)  # 選択されたプラントのクラスを取得
        plant_cost = plant_data[self.selected_plant]["cost"]
        plant_items = plant_data[self.selected_plant]["item"]  # 必要なアイテムの辞書を取得（なければ空辞書）

        
        if item_consume(plant_cost, plant_items, self):
            # プラントを追加
            plant_class(pos_x, pos_y, self)
            self.plant_added = True  # プラントが追加されたフラグ
            
    def pause_screen(self):
    # **ゲームの最新フレームを保持（再描画しない）**
        self.pause_start_time = pygame.time.get_ticks()  # 一時停止開始時間を記録
        clock = pygame.time.Clock()
        pause_overlay = screen.copy()  # 現在の画面を保存
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))  # 半透明の黒を適用

        pause_overlay.blit(overlay, (0, 0))  # 半透明の黒を合成
        screen.blit(pause_overlay, (0, 0))  # 画面に描画z

        while self.paused:

            pause_text = self.font.render("Paused", True, (255, 255, 255))
            screen.blit(pause_text, (screen_width // 2 - 40, screen_height // 2))

            self.buttons.draw(screen)  # ボタンを表示
                    
            pygame.display.update()  # 画面を更新

            button_clicked = False  # ボタンが押されたかどうかのフラグ

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                        
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                for button in self.buttons:
                                    if button.rect.collidepoint(event.pos):
                                        button.Process()
                                        button_clicked = True  # ボタンが押されたらフラグを変更
                                        break  # ボタンが押されたらループを抜ける
                                
                                if not button_clicked:
                                    self.paused = False  # どのボタンも押されなかったらゲームを再開
                clock.tick(30)
            
        self.paused_duration += pygame.time.get_ticks() - self.pause_start_time

    def zoom_screen(self):
        self.zoom_start_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()  # ループの外で定義
        screen_overlay = screen.copy()  # 現在の画面を保存
        back_image = pygame.image.load("Assets/Back.png")

        zoom_image = []
        for i in range(45):
            zoom_path = pygame.image.load(f"Assets/ZoomScreen/ZoomScreen_{i:05}.png")
            zoom_image.append(zoom_path)
        self.zoom_frame = 0

        screen.blit(back_image, (-350, -450))

        # **オフセットの初期化**
        init_dif_x, init_dif_y = 0, 0

        self.plant_levelup()

        while self.zooming:
            step = 0.08  # 1回のズーム変化量（0.08ずつ拡大/縮小）

            # **プラントを中心にズームする**
            plant_x, plant_y = self.zoom_to.rect.center

            # **ズーム後のスクリーンサイズ**
            zoomed_width = int(screen_width * self.zoom_factor)
            zoomed_height = int(screen_height * self.zoom_factor)

            # **ズーム時のオフセット計算（ズーム倍率によるズレを補正）**
            zoom_dif_x = (plant_x * self.zoom_factor - plant_x)
            zoom_dif_y = (plant_y * self.zoom_factor - plant_y)

            # **ズームの処理**
            if self.zooming_in:
                self.zoom_factor += step
                # **オフセットをスムーズに補間**
                init_dif_x += (screen_width // 2 - plant_x - init_dif_x) * step
                init_dif_y += (screen_height // 2 - plant_y - init_dif_y) * step
                if self.zoom_factor >= self.zoom_target:
                    self.zoom_factor = self.zoom_target
                    self.zooming_in = False
                    self.zooming_out = False

            # **画面全体をズーム**
            zoomed_surface = pygame.transform.scale(screen_overlay, (zoomed_width, zoomed_height))

            # **ズームした画面をオフセットで描画**
            screen.blit(back_image, (-100 - zoom_dif_x + init_dif_x, -450 - zoom_dif_y + init_dif_y))
            screen.blit(zoomed_surface, (-zoom_dif_x + init_dif_x, -zoom_dif_y + init_dif_y))

            path = zoom_image[self.zoom_frame]
            screen.blit(path, (0, 0))

            # **フレームの進行**
            if not self.zooming_out:
                self.zoom_frame = min(self.zoom_frame + 1, 15)
            else:
                break  # ズームアウトの処理へ移行

            # **イベント処理**
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.start_zoom_out()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左クリック
                        # ボタンの処理
                        for button in self.zoom_buttons:
                            if button.rect.collidepoint(event.pos):
                                button.Process()

                                break  # クリック処理をボタンで完了するためにループを抜ける
            
            text = self.font.render(f"{self.zoom_to.name}", True, WHITE)
            screen.blit(text, (610, 30))
            screen.blit(art_dict[self.zoom_to.name].image[0], (400, -150))
            screen.blit(self.arrow_image, (630, 130))
            text = self.font.render(f"{self.upper_class_name}", True, WHITE)
            screen.blit(text, (610, 210))
            screen.blit(art_dict[self.upper_class_name].image[0], (400, 30))

            text = self.font_small.render("Level Up", True, WHITE)
            screen.blit(text, (620, 340))
            text = self.font_small.render("Requirements", True, WHITE)
            screen.blit(text, (600, 360))
            
            self.plant_cost = plant_data[self.zoom_to.upper_plant]["cost"]
            self.plant_items = plant_data[self.zoom_to.upper_plant]["item"]

            i = 0
            text_item((600, 390), "points", self.points, self.plant_cost, self, self.font_small)
            for key, value in self.plant_items.items(): #辞書にアイテムを追加
                text_item((610, 410 + i * 20), key, self.item[key], value, self, self.font_small)
                i += 1    

            text = self.font_small.render("Level Up?", True, WHITE)
            screen.blit(text, (455, 450))

            #名前表示
            self.big_font = pygame.font.SysFont(None, 100)
            text = self.big_font.render(f"{self.zoom_to.name}", True, self.zoom_to.color)
            screen.blit(text, (10, 400))

            self.zoom_buttons.draw(screen)
            for text in self.texts:
                text.draw(screen)

            pygame.display.flip()
            clock.tick(30)

        # **ズームアウトの処理**
        while self.zooming_out:
            step = 0.08
            self.zoom_factor -= step

            # **オフセットをスムーズに戻す**
            init_dif_x -= init_dif_x * step
            init_dif_y -= init_dif_y * step

            # **ズームが完了したらループを抜ける**
            if self.zoom_factor <= 1.0:
                self.zoom_factor = 1.0
                self.zooming_out = False
                break

            # **ズームアウト時のアニメーション**
            self.zoom_frame = min(self.zoom_frame + 1, 44)

            # **ズームアウト時の描画**
            zoomed_width = int(screen_width * self.zoom_factor)
            zoomed_height = int(screen_height * self.zoom_factor)
            zoom_dif_x = (plant_x * self.zoom_factor - plant_x)
            zoom_dif_y = (plant_y * self.zoom_factor - plant_y)
            zoomed_surface = pygame.transform.scale(screen_overlay, (zoomed_width, zoomed_height))
            init_dif_x *= (1 - step)  # 徐々にゼロに戻す
            init_dif_y *= (1 - step)  # 徐々にゼロに戻す

            screen.blit(back_image, (-100 - zoom_dif_x + init_dif_x, -450 - zoom_dif_y + init_dif_y))
            screen.blit(zoomed_surface, (-zoom_dif_x + init_dif_x, -zoom_dif_y + init_dif_y))

            path = zoom_image[self.zoom_frame]
            screen.blit(path, (0, 0))

            pygame.display.flip()
            clock.tick(30)
        
        self.zoom_duration += pygame.time.get_ticks() - self.zoom_start_time

    def plant_levelup(self):

        self.upper_class = globals().get(self.zoom_to.upper_plant)
        upper_plant = self.upper_class(0, 0, self)
        self.upper_class_name = upper_plant.name
        upper_plant.kill()

        new_button = LevelupButton(self.zoom_to, self.upper_class, self)
        self.zoom_buttons.add(new_button)
        new_button = noLevelupButton(self.zoom_to, self)
        self.zoom_buttons.add(new_button)

    def start_zoom_in(self, plant):
        self.zoom_to = plant
        self.zooming = True
        self.zooming_in = True
        self.zooming_out = False  # **ズームアウトのフラグをリセット**

    def start_zoom_out(self):
        self.zooming_out = True
        self.zooming = False  # **ズームインを停止**
        self.zoom_frame = 30  # **ズームアウト用のアニメーションフレーム設定**

    def game_over_screen(self):
        """ゲームオーバー画面の描画"""
        screen.fill((0, 0, 0))  # 黒背景
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))  # 赤いゲームオーバーテキスト
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))  # 白いリスタートメッセージ

        screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2 - 50))
        screen.blit(restart_text, (screen_width // 2 - 120, screen_height // 2 + 20))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # "R"キーで再スタート
                        waiting = False

                        # ここで現在のインスタンス(self)を終了し、新しいmaingameインスタンスを生成
                        del self  # 現在のインスタンスを削除
                        new_game = maingame()  # 新しいインスタンスを生成
                        new_game.game_loop()  # 新しいインスタンスでゲームを再スタート
                        break  # イベントループを抜けて再スタート  

game = maingame()
game.game_loop()