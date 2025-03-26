import pygame
import os

item_image_dict = \
    {"fire element_image": pygame.image.load("Assets/fire element.png"),  \
    "water element_image": pygame.image.load("Assets/water element.png"),  \
    "thunder element_image": pygame.image.load("Assets/thunder element.png")}

class LoadedImage():
    def __init__(self, animation, path, frames, form):
        self.animation = animation
        self.frames = frames
        self.image = []
        if animation:
            for i in range(frames):  
                img_path = f"{path}_{i:05}.png"
                if os.path.exists(img_path):
                    frame = pygame.image.load(img_path)
                    if i == 0:
                        self.art_rect = frame.get_rect()
                        self.art_dif_x = (self.art_rect.width - form[0])/2
                        self.art_dif_y = (self.art_rect.height - form[1])/2
                    self.image.append(frame)
                else:
                    print(f"Warning: {img_path} not found")
        else:
            frame = pygame.image.load(f"{path}.png")
            self.image.append(frame)
            self.art_rect = frame.get_rect()
            self.art_dif_x = (self.art_rect.width - form[0])/2
            self.art_dif_y = (self.art_rect.height - form[1])/2

PLANT = (80, 80)
PEA = (10, 5)


art_dict = {"Plant": LoadedImage(False, "Assets/Plant", 1, PLANT), "Pea": LoadedImage(False, "Assets/Pea", 1, PEA),  \
            "StrongPlant": LoadedImage(True, "Assets/StrongPlant/StrongPlant", 40, PLANT), "BluePea": LoadedImage(False, "Assets/Pea", 1, PEA), \
            "Rock": LoadedImage(False, "Assets/Rock", 1, PLANT), \
            "Obsidian": LoadedImage(True, "Assets/Obsidian/Obsidian", 70, PLANT), "ObsidianAttack": LoadedImage(True, "Assets/ObsidianAttack/ObsidianAttack", 30, PLANT),\
            "Fire": LoadedImage(True, "Assets/Fire/Fire", 70, PLANT), "FirePea": LoadedImage(True, "Assets/FirePea/FirePea", 25, PEA), "FireTrap": LoadedImage(True, "Assets/FireTrap/FireTrap", 25, PLANT), \
            "Water": LoadedImage(True, "Assets/Water/Water", 50, PLANT), "WaterPea": LoadedImage(True, "Assets/WaterPea/WaterPea", 30, PEA), \
            "Thunder": LoadedImage(True, "Assets/Thunder/Thunder", 50, PLANT), "ThunderPea": LoadedImage(True, "Assets/ThunderPea/ThunderPea", 50, PEA), \
            "Zombie": LoadedImage(False, "Assets/Zombie", 1, PLANT), "ZombieAttack": LoadedImage(True, "Assets/ZombieAttack/ZombieAttack", 30, PEA), \
            "YellowItem": LoadedImage(True, "Assets/YellowItem/YellowItem", 50, (20, 20))}

plant_data = {
    "Plant": {"cost": 10, "item": {}},
    "StrongPlant": {"cost": 30, "item": {}},
    "Rock": {"cost": 5, "item": {}},
    "Obsidian": {"cost": 30, "item": {}},
    "Fire": {"cost": 20, "item": {"fire element": 2}},
    "Water": {"cost": 15, "item": {"water element": 2}},
    "Thunder": {"cost": 15, "item": {"thunder element": 2}}
}


