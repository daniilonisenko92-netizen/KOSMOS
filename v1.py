import pygame as pg
import random

YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 1920
HEIGHT = 1080


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


class EnemyBullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((5, 15))
        self.image.fill(RED)
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

    def update(self, player_rect, enemy_bullets_group):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-200, -50)
            self.speed = random.randint(3, 7)

        if self.rect.left < player_rect.centerx < self.rect.right and self.rect.bottom < player_rect.top:
            current_time = pg.time.get_ticks()
            if current_time - self.last_shot > self.fire_delay:
                self.shoot(enemy_bullets_group)
                self.last_shot = current_time

    def shoot(self, enemy_bullets_group):
        new_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        enemy_bullets_group.add(new_bullet)


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

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.rect.x -= self.speed
        if keys[pg.K_d]:
            self.rect.x += self.speed
        if keys[pg.K_w]:
            self.rect.y -= self.speed
        if keys[pg.K_s]:
            self.rect.y += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        current_time = pg.time.get_ticks()
        if current_time - self.last_shot > self.fire_delay:
            self.shoot()
            self.last_shot = current_time

        self.bullet_group.update()

    def shoot(self):
        new_bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullet_group.add(new_bullet)

    def draw(self, screen):
        self.bullet_group.draw(screen)
        screen.blit(self.image, self.rect)


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Космический Симулятор")
clock = pg.time.Clock()

player_img = pg.image.load("fvubakamd1pc1.png").convert_alpha()
kosmos_img = pg.image.load("kosmos_img.png").convert_alpha()
vrag_img = pg.image.load("enemy.png").convert_alpha()

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
                running = False

    kosmos.update()
    player.update()
    
    for vrag in enemies:
        vrag.update(player.rect, enemy_bullets)
        
    enemy_bullets.update()

    kosmos.draw(screen)
    enemies.draw(screen)
    enemy_bullets.draw(screen)
    player.draw(screen)

    pg.display.flip()
    clock.tick(60)

pg.quit()