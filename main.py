import os
import random
import pygame


# ###################### Module Initialisation ##################
# pygame.mixer.init(48000, 32, 1, 1024)
HEIGHT = 750
WIDTH = 900
pygame.font.init()
pygame.display.init()

# ########################## Assets ############################
SHIP1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "main_ship.png")), (100, 100))
SHIP2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "spaceship.png")), (130, 100))
BLAST = pygame.transform.scale(pygame.image.load(os.path.join("assets", "blast.png")), (100, 100))
MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "missile1.png")), (10, 40))
MINION = pygame.image.load(os.path.join("assets", "minion.png"))
BACKGROUND = pygame.image.load(os.path.join("assets", "background-black.png"))
ICON = pygame.image.load(os.path.join("assets", "small.png"))
# BG_MUSIC = pygame.mixer.music.load("sg.mp3")

# ####################### Display initialisation #################

GameWindow = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders | By Shivansh Kothari")
pygame.display.set_icon(ICON)


class Weapon:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.bodyImg = img
        self.mask = pygame.mask.from_surface(self.bodyImg)

    def draw(self, window):
        window.blit(self.bodyImg, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self):
        return not (HEIGHT >= self.y >= 0)

    def collision(self, entity):
        return collide(self, entity)


class Entity:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.bodyImg = None
        self.weaponImg = None
        self.weapons = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.bodyImg, (self.x, self.y))
        for weapon in self.weapons:
            weapon.draw(window)

    def move_missiles(self, vel, entities):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen():
                self.weapons.remove(weapon)
            else:
                for entity in entities:
                    if weapon.collision(entity):
                        if entity.bodyImg == SHIP1:
                            entity.health -= 10

                        entities.remove(entity)
                        try:
                            self.weapons.remove(weapon)
                        except ValueError:
                            print("")

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            self.weapons.append(Weapon(self.x+self.get_width()/2-5, self.y-40, self.weaponImg))
            self.cooldown_counter = 1

    def get_width(self):
        return self.bodyImg.get_width()

    def get_height(self):
        return self.bodyImg.get_height()


class PlayerShip(Entity):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.bodyImg = SHIP1
        self.weaponImg = MISSILE
        self.player_vel = 5
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.bodyImg)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.get_height() + 10, self.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.get_height() + 10, self.get_width() * self.health/self.max_health, 10))


class Enemy(Entity):
    ENEMIES = [
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "small.png")), (50, 50)),
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "medium.png")), (80, 80)),
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "green_boss.png")), (150, 150))]

    def __init__(self, x, y, version, health=100):
        super().__init__(x, y, health)
        self.bodyImg, self.weaponImg = self.ENEMIES[version], MISSILE
        if version == 3:
            self.health = 200
        self.mask = pygame.mask.from_surface(self.bodyImg)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown_counter == 0:
            self.weapons.append(Weapon(self.x+self.get_width()/2-5, self.y+self.get_height()+2, self.weaponImg))
            self.cooldown_counter = 1

def collide(entity1, entity2):
    x_offset = entity2.x - entity1.x
    y_offset = entity2.y - entity1.y
    return entity1.mask.overlap(entity2.mask, (x_offset, y_offset)) != None


def main():
    running = True
    FPS = 30
    level = 0
    lives = 3
    Lost = False
    lost_count = 0
    game_clock = pygame.time.Clock()
    player = PlayerShip(300, 620)
    enemies = []
    coordinates = [()]*100
    wave_length = 0
    enemy_vel = 2
    missile_vel = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)


    def drawScreen():
        GameWindow.blit(pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT)), (0, 0))

        for enemy in enemies:
            enemy.draw(GameWindow)

        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        # high_score_label = main_font.render(f"High score:", 1, (255,255,255))
        GameWindow.blit(lives_label, (10, 10))
        GameWindow.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        # GameWindow.blit(high_score_label, (WIDTH - level_label.get_width() - 10, 20))
        player.draw(GameWindow)
        if Lost:
            game_over = lost_font.render("Game Over", 1, (255, 255, 255))
            GameWindow.blit(game_over, (WIDTH/2 - game_over.get_width()/2, 350))

        pygame.display.update()

    while running:
        game_clock.tick(FPS)
        drawScreen()

        if lives == 0 or player.health <= 0:
            Lost = True
            if lives > 0:
                player.bodyImg = BLAST
            lost_count += 1

        if Lost:
            if lost_count == FPS * 2:
                running = False

        if len(enemies) == 0:
            max = 0
            level += 1
            if level % 3 == 0:
                health = 130
                player.bodyImg = SHIP2
            wave_length += 5
            for i in range(wave_length):
                enemy_dimensions = random.randrange(0, 2)
                coordinates[i] = (random.randrange(50, WIDTH - [50, 100, 250][enemy_dimensions] - 50), random.randrange(-1500, -100))
                if coordinates[i][1] < max:
                    max = coordinates[i][1]
                enemies.append(Enemy(coordinates[i][0],
                                     coordinates[i][1], enemy_dimensions))

            for i in range(level-1):
                enemy_dimensions = (random.randrange(50, WIDTH - 300), random.randrange(-1500, max+100))
                enemies.append(Enemy(enemy_dimensions[0],
                                     enemy_dimensions[1]-1, 2, 200))
                enemies.append(Enemy(enemy_dimensions[0],
                                     enemy_dimensions[1], 2, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player.player_vel > 0 and not Lost:  # left
            player.x -= player.player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player.player_vel + player.get_width() < WIDTH and not Lost:  # right
            player.x += player.player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_missiles(missile_vel, [player])
            if random.randrange(0, 4*FPS) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y - enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_missiles(-missile_vel, enemies)


def main_menu():
    header_font = pygame.font.SysFont("comicsans", 100)
    closed = False
    while not closed:
        GameWindow.blit(pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT)), (0, 0))
        start_label = header_font.render("Click 2 Start", 1, (255, 255, 255))
        GameWindow.blit(start_label, (WIDTH/2 - start_label.get_width()/2, 350))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
            pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main_menu()
