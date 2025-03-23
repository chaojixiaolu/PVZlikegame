import pygame
import random
from Character import * 
from Back_Process import *
import objgraph
import gc
import graphviz



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


        self.points = 50  
        self.Plant_cost = 10
        self.Rock_cost = 5
        self.Fire_cost = 20
        self.Water_cost = 15
        self.Thunder_cost = 15

       

        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.plants = pygame.sprite.Group()
        self.nuts = pygame.sprite.Group()
        self.yellow_items = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.errors = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()

        self.plant = Plant(GRID_CENTER[2][1][0], GRID_CENTER[2][1][1], self)
        self.all_sprites.add(self.plant)
        self.plants.add(self.plant)

        self.zombie = Zombie(screen_width, GRID_CENTER[0][random.randint(0, GRID_V_Number-1)][1], self)
        self.all_sprites.add(self.zombie)
        self.zombies.add(self.zombie)

        self.background = pygame.image.load("Assets/BackGround1.png").convert()
        screen.blit(self.background, (0,0))
        Plantbutton(self)
        Rockbutton(self)
        PauseButton(self)
        Firebutton(self)
        Waterbutton(self)
        Thunderbutton(self)

        
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.current_time = pygame.time.get_ticks()

             # **ゲームオーバーならループを抜ける**
            if self.deadcount > self.deadline:
                running = False
                break  # メインループを抜ける

            # **一時停止処理**
            if self.paused:
                # **ゲームの最新フレームを保持（再描画しない）**
                pause_overlay = screen.copy()  # 現在の画面を保存
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 50))  # 半透明の黒を適用

                pause_overlay.blit(overlay, (0, 0))  # 半透明の黒を合成
                screen.blit(pause_overlay, (0, 0))  # 画面に描画

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

                    clock.tick(15)  # 低フレームレートで処理

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
                                            plant.leveluptext = True  # レベルアップテキストを表示
                                            break  # それ以上の処理を避ける

                                    for plant in self.nuts:
                                        # マウスクリックがプラントに当たった場合
                                        if plant.rect.collidepoint(event.pos):
                                            plant.leveluptext = True  # レベルアップテキストを表示
                                            break  # それ以上の処理を避ける       

                                        # もしクリックした位置に既存のプラントがない場合
                                    if self.sprite_positions.get(mouse_grid) is None and not self.plant_added:
                                        plant_class = globals().get(self.selected_plant)  # 選択されたプラントのクラスを取得
                                        plant_cost = getattr(self, f"{self.selected_plant}_cost", None)  # コストを取得

                                        if plant_class and plant_cost is not None and self.points >= plant_cost:
                                            self.points -= plant_cost  # ポイントを減算
                                            plant_class(mouse_grid[0], mouse_grid[1], self)  # インスタンス作成
                                            self.plant_added = True  # プラントが追加されたフラグ


                                        # ポイントが足りない場合、エラーメッセージを表示
                                        elif not self.plant_added:
                                            self.error = Error(screen, "You don't have enough points!")
                                            self.errors.add(self.error)
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
                self.all_sprites.remove(zombie)
                del zombie


            screen.blit(self.background, (0,0))
            # screen.fill(BLACK)
            # bg_surface = draw_background()
            # screen.blit(bg_surface, (0, 0))

            for trap in self.traps:
                drawart(screen, trap)
            self.all_sprites.draw(screen)

            for plant in self.all_sprites:  #絵を描写
                drawart(screen, plant)
            
            for plant in self.plants: #HP
                draw_hp(screen, plant, GREEN)
            for zombie in self.zombies:
                draw_hp(screen, zombie, RED)

            # スコア表示
            score_text = self.font.render(f"Points: {self.points}", True, BLACK)
            screen.blit(score_text, (10, 120))
            
            # モード表示
            mode_text = self.font.render(f"Mode: {self.selected_plant}", True, BLACK)
            screen.blit(mode_text, (screen_width - 200, screen_height - 40))

            # **時間の表示**
            elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # ミリ秒 → 秒
            time_text = self.font.render(f"Time: {elapsed_time} s", True, (0, 0, 0))  # 黒色
            screen.blit(time_text, (screen_width - 150, 120))  # 右上に表示

            # カウント表示
            count_text = self.font.render(f"{self.deadcount}/{self.deadline}", True, RED)
            screen.blit(count_text, (10, 150))

            """現在のレベルを表示"""
            # 画面を黒で塗りつぶし
            level_text = self.font.render(f"Level: {self.current_level}", True, BLACK)
            screen.blit(level_text, (10, screen_height -50 ))


            for zombie in self.zombies:
                zombie.message(screen)
                if zombie.collide and zombie.collide_Nut and not zombie.collide_Nut.alive():
                    zombie.collide = False  # ナッツが消えたら再び移動
                    zombie.collide_Nut = None
                drawattack(screen, zombie)

            for plant in self.plants:
                if plant.leveluptext:
                    plant.show_levelup_text()
                    plant.leveluptext = False
                drawattack(screen, plant)
       
            for plant in self.nuts:
                if plant.leveluptext:
                    plant.show_levelup_text()
                    plant.leveluptext = False
                drawattack(screen, plant)

            self.buttons.draw(screen)
            self.buttons.update()
            self.traps.draw(screen)
            for error in self.errors:
                error.draw()

            for plant in self.plants:  # 衝突処理(タネ、ゾンビ)
                for pea in plant.peas:  # タネとゾンビ衝突
                    collided_zombie = pygame.sprite.spritecollideany(pea, self.zombies)
                    if collided_zombie:
                        pea.collide(collided_zombie)
                        collided_zombie.message_text = "Hit"
                        if collided_zombie.hp <= 0:
                            collided_zombie.kill()  # HPが0になったら削除
                            del collided_zombie

            for plant in self.plants:  # 衝突処理(プラント, ゾンビ)
                collided_zombie = pygame.sprite.spritecollideany(plant, self.zombies)
                if collided_zombie:
                    collided_zombie.damage_to_plant(plant)
                    collided_zombie.is_attacking = plant
                    
            for Nut in self.nuts:  # 衝突処理(rock、ゾンビ)
                collided_zombie = pygame.sprite.spritecollideany(Nut, self.zombies)
                if collided_zombie:
                    collided_zombie.collide_stop(Nut)
                    collided_zombie.is_attacking = Nut

            for trap in self.traps:  # トラッぷとゾンビ衝突
                    collided_zombie = pygame.sprite.spritecollideany(trap, self.zombies)
                    if collided_zombie:
                        trap.collide(collided_zombie)
                        collided_zombie.message_text = "Hit"
                        if collided_zombie.hp <= 0:
                            collided_zombie.kill()  # HPが0になったら削除
                            collided_zombie.kill()
             
            self.traps.update()
            self.all_sprites.update()
            self.errors.update()
            
            pygame.display.flip()

            clock.tick(30)
            gc.collect()  # ガーベジコレクションを手動で実行
            # objgraph.show_growth()
            
        self.game_over_screen()  # ゲームオーバー画面を表示

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