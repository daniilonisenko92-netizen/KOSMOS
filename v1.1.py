import pygame as pg
import random
from PIL import Image

YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
LaserPurple = (219, 10, 255)  

WIDTH = 1980
HEIGHT = 1080

score = 0 
pg.font.init()
my_font = pg.font.SysFont("Impact", 64)
level = 1
game_state = "menu"
damage_taken = False

class Kosmos:
    def __init__(self, image, speed):
        self.image = pg.transform.scale(image, (WIDTH, HEIGHT))
        self.speed = speed
        self.y1 = 0
        self.y2 = -HEIGHT

    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, screen):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
    
    def change_back(self, new_image):
        self.image = pg.transform.scale(new_image, (WIDTH, HEIGHT))


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -15

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class BigBullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((5, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -8
        self.damage = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((5, 15))
        self.image.fill(LaserPurple)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 10

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class VragKorabel(pg.sprite.Sprite):
    def __init__(self, image):
        super().__init__() 
        self.image = pg.transform.scale(image, (80, 80)).convert_alpha()
        self.rect = self.image.get_rect()
        
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-200, -50)
        self.speed = random.randint(3, 7)

        self.fire_delay = 500
        self.last_shot = pg.time.get_ticks()
        
        self.max_hp = 30
        self.hp = 30

    def update(self, player_rect, enemy_bullets_group):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset_position()
        
        if self.rect.left < player_rect.centerx < self.rect.right and self.rect.bottom < player_rect.top:
            current_time = pg.time.get_ticks()
            if current_time - self.last_shot > self.fire_delay:
                self.shoot(enemy_bullets_group)
                self.last_shot = current_time

    def shoot(self, enemy_bullets_group):
        new_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        enemy_bullets_group.add(new_bullet)

    def reset_position(self):
        global level
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-200, -50)
        base_speed = random.randint(3, 7)
        self.speed = base_speed * (1.2 ** (level - 1))
        self.max_hp = int(30 * (1.2 ** (level - 1)))
        self.hp = self.max_hp

    def draw_hp(self, surface):
        pg.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 12, 80, 6))
        hp_width = int(80 * (self.hp / self.max_hp))
        if self.hp > 0:
            pg.draw.rect(surface, RED, (self.rect.x, self.rect.y - 12, hp_width, 6))


class Player(pg.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pg.transform.scale(image, (100, 100)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 50
        self.speed = 15

        self.bullet_group = pg.sprite.Group()
        self.fire_delay = 150  
        self.last_shot = pg.time.get_ticks()

        self.dash_speed = 45       
        self.dash_duration = 100   
        self.dash_timer = 0        
        self.dash_dir = 0          

        self.max_hp = 100
        self.hp = 100
        self.last_big_shot = 0  

    def update(self):
        current_time = pg.time.get_ticks()
        keys = pg.key.get_pressed()

        if keys[pg.K_LSHIFT] and self.dash_timer == 0:
            if keys[pg.K_a]:
                self.dash_dir = -1
                self.dash_timer = current_time
            elif keys[pg.K_d]:
                self.dash_dir = 1
                self.dash_timer = current_time

        if self.dash_timer != 0 and current_time - self.dash_timer < self.dash_duration:
            self.rect.x += self.dash_speed * self.dash_dir
        else:
            self.dash_timer = 0  
            self.dash_dir = 0
            if keys[pg.K_a]:
                self.rect.x -= self.speed
            if keys[pg.K_d]:
                self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if keys[pg.K_SPACE] or pg.mouse.get_pressed()[0]: 
            if current_time - self.last_shot > self.fire_delay:
                self.shoot()
                self.last_shot = current_time

        if pg.mouse.get_pressed()[2]:  
            if current_time - self.last_big_shot > 2000:  
                new_big_bullet = BigBullet(self.rect.centerx, self.rect.top)
                self.bullet_group.add(new_big_bullet)
                self.last_big_shot = current_time  

        self.bullet_group.update()

    def shoot(self):
        new_bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullet_group.add(new_bullet)

    def draw(self, screen):
        self.bullet_group.draw(screen)
        screen.blit(self.image, self.rect)

    def draw_hp(self, surface):
        x = 50
        y = HEIGHT - 50
        width = 200
        height = 15

        pg.draw.rect(surface, BLACK, (x, y, width, height))
        hp_width = int(width * (self.hp / self.max_hp))
        if self.hp > 0:
            if self.max_hp >= 999999:
                current_color = YELLOW
            else:
                current_color = GREEN   
                
            pg.draw.rect(surface, current_color, (x, y, hp_width, height))


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Космический Симулятор")
clock = pg.time.Clock()

try:
    pil_img = Image.open("avatar.png").convert("RGBA")
    avatar_img = pg.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode)
    pg.display.set_icon(avatar_img)
    player_img = pg.image.load("fvubakamd1pc1.png").convert_alpha()
    kosmos_img = pg.image.load("kosmos_img.png").convert_alpha()
    vrag_img = pg.image.load("enemy.png").convert_alpha()
    vrag_img1 = pg.image.load("vrag_img1.png").convert_alpha()
    vrag_img2 = pg.image.load("vrag_img2.png").convert_alpha()
    vrag_img3 = pg.image.load("vrag_img3.png").convert_alpha()
    vrag_img4 = pg.image.load("vrag_img4.png").convert_alpha()
    kosmos_img2 = pg.image.load("nebo2.png").convert_alpha()
    kosmos_img3 = pg.image.load("kosmos_img3.png").convert_alpha()
    kosmos_img4 = pg.image.load("index.png").convert_alpha()
    kosmos_img5 = pg.image.load("kosmos_img5.png").convert_alpha
    menu_bg_img = pg.image.load("kosmos_img.png").convert_alpha()
    menu_bg_img = pg.transform.scale(menu_bg_img, (WIDTH, HEIGHT))
except FileNotFoundError as e:
    print(f"Ошибка загрузки картинок! {e}")
    pg.quit()
    exit()

kosmos = Kosmos(kosmos_img, speed=5)
player = Player(player_img)
enemies = pg.sprite.Group()
for _ in range(5):
    enemies.add(VragKorabel(vrag_img))
enemy_bullets = pg.sprite.Group()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if game_state == "game":
                    game_state = "menu"
                else:
                    running = False
            if game_state == "menu" and event.key == pg.K_RETURN:
                game_state = "game"
                kosmos.change_back(kosmos_img)
            if game_state == "menu" and event.key == pg.K_SPACE:
                game_state = "game"
                player.max_hp = 100
                player.hp = player.max_hp
                score = 0
                level = 1
                damage_taken = False
                kosmos.change_back(kosmos_img)
                for vrag in enemies:
                    vrag.reset_position()

    if game_state == "game":
        kosmos.update()
        player.update()   
        for vrag in enemies:
            vrag.update(player.rect, enemy_bullets)
        enemy_bullets.update()
        
        for bullet in player.bullet_group:
            hit_enemies = pg.sprite.spritecollide(bullet, enemies, False)
            for vrag in hit_enemies:
                if hasattr(bullet, 'damage'):
                    vrag.hp -= bullet.damage
                else:
                    vrag.hp -= 10
                bullet.kill()
                if vrag.hp <= 0: 
                    score += 50
                    vrag.reset_position()

                    new_level = (score // 500) + 1
                    if new_level > level:
                        level = new_level
                        if level == 1:
                            kosmos.change_back(kosmos_img)
                        elif level == 2:
                            kosmos.change_back(kosmos_img2)
                        if level == 2:
                            enemies.add(VragKorabel(vrag_img1))
                        elif level == 3:
                            kosmos.change_back(kosmos_img3)
                        if level == 3:
                            enemies.add(VragKorabel(vrag_img2))
                        elif level == 4:
                            kosmos.change_back(kosmos_img4)
                        if level == 4:
                            enemies.add(VragKorabel(vrag_img3))
                        if level >= 3 and not damage_taken:
                            player.max_hp = 999999  
                            player.hp = player.max_hp
                            print("РЕЖИМ БОГА АКТИВИРОВАН!")
                        elif level > 4:
                            if player.max_hp >= 999999:
                                player.max_hp = 100
                                player.hp = player.max_hp
                                print("Режим бога окончен!")
                        elif level == 5:
                            enemies.add(VragKorabel(vrag_img4))
                        if level == 5:
                            kosmos.change_back(kosmos_img5)

        hit_player_bullets = pg.sprite.spritecollide(player, enemy_bullets, True)
        for bullet in hit_player_bullets:
            
            if player.max_hp < 999999:
                damage_taken = True  
                player.hp -= 15
                
            if player.hp <= 0:
                print("Игра окончена! Твой корабль уничтожен.")
                game_state = "menu"
                
                player.max_hp = 100 
                player.hp = player.max_hp 
                score = 0
                level = 1
                damage_taken = False  
                kosmos.change_back(kosmos_img)
                enemies.empty()
                for _ in range(5):
                    enemies.add(VragKorabel(vrag_img))
                break
                    
        screen.fill(BLACK)
        kosmos.draw(screen)
        enemies.draw(screen)
        enemy_bullets.draw(screen)
        player.draw(screen)  
        player.draw_hp(screen)
        for vrag in enemies:
            vrag.draw_hp(screen)
            
        score_text = my_font.render(f"Очки: {score}", True, WHITE)
        screen.blit(score_text, (50, 50))

        level_text = my_font.render(f"Уровень: {level}", True, YELLOW)
        screen.blit(level_text, (50, 120))
    
    elif game_state == "menu":
        screen.blit(menu_bg_img, (0, 0)) 
        title_font = pg.font.SysFont("Arial", 64)
        title_text = title_font.render("КОСМИЧЕСКИЙ МАЗАХИЗМ", True, WHITE)
        hint_text = my_font.render("Нажмите ENTER для старта игры", True, BLUE)
        restart_hint_text = my_font.render("Нажмите ПРОБЕЛ для перезапуска", True, YELLOW)
        exit_text = my_font.render("Нажмите ESC для выхода", True, RED)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 60))
        screen.blit(restart_hint_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 120))

    pg.display.flip()
    clock.tick(60)

pg.quit()