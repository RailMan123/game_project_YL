import pygame
import os
import random
import sys

pygame.init()
size = width, height = 1050, 750
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
screen.fill((0, 0, 255))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
fishes = pygame.sprite.Group()
plants = pygame.sprite.Group()
speedups = [20, 30, 40, 60, 80, 100]
healthups = [20, 40, 60, 80, 100]
FPS = 100
player = 0
player_pos = (0, 0)


def terminate():
    pygame.quit()
    sys.exit()


def dats_write():
    global file
    file = open('stat_datas', 'w')
    file.write(str(gold) + '\n')
    file.write(str(player.speedlevel) + '\n')
    file.write(str(int(player.maxhealth / 10000)))
    file.close()
    for sprite in all_sprites:
        sprite.kill()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


button = load_image('button.png', -1)
monet = load_image('monet.png', -1)
monet = pygame.transform.scale(monet, (50, 50))
fon = pygame.transform.scale(load_image('background.jpg'), (width, height))
screen.blit(fon, (0, 0))


def cut_sheet(self, sheet, columns, rows, frames):
    self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))


class Sharky(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global player
        global player_pos
        super().__init__(all_sprites)
        self.swimframes = []
        self.moveframes = []
        self.eatframes = []
        file = open('stat_datas').read()
        file = file.split('\n')
        self.speedlevel = int(file[1])
        for i in range(1, 6):
            sheet = load_image(f'bluesharkswim(' + str(i) + ').png', colorkey=-1)
            self.swimframes.append(sheet.subsurface(pygame.Rect(
                (0, 0), sheet.get_rect().size)))
        for i in range(1, 11):
            sheet = load_image(f'bluesharkmove' + str(i) + '.png', colorkey=-1)
            self.moveframes.append(sheet.subsurface(pygame.Rect(
                (0, 0), sheet.get_rect().size)))
        cut_sheet(self, load_image('bluesharkeat.png', colorkey=-1), 2, 1, self.eatframes)
        self.cur_frame = 0
        self.image = self.swimframes[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.health = int(file[2]) * 10000
        self.maxhealth = int(file[2]) * 10000
        player = self
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.mov = 0
        player_pos = (player.rect.x + player.rect.w // 2, player.rect.y + player.rect.h // 2)

    def update(self):
        self.count += 1
        self.health -= 5
        if self.count == 25:
            self.cur_frame = (self.cur_frame + 1) % len(self.swimframes)
            if self.mov == 9:
                self.image = pygame.transform.flip(self.swimframes[self.cur_frame], 90, 0)
            else:
                self.image = self.swimframes[self.cur_frame]
            self.count = 0

    def movement(self, dir):
        if dir == -1:
            self.image = self.moveframes[self.mov]
            self.mov += 1
        elif dir == 1:
            self.image = self.moveframes[self.mov]
            self.mov -= 1

    def move(self):
        for sprite in all_sprites:
            camera.apply(sprite)


class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__(all_sprites)
        self.add(fishes)
        self.swimframes = []
        if type == 'yellowfish':
            self.type = 'yellow'
            cut_sheet(self, load_image('yellowfishswim.png', colorkey=-1), 6, 1, self.swimframes)
            self.swimstyle = [1, 0]
        elif type == 'goldfish':
            self.type = 'gold'
            cut_sheet(self, load_image('goldfishswim.png', colorkey=-1), 6, 1, self.swimframes)
            self.swimstyle = [-1, 0]

        self.cur_frame = 0
        self.image = self.swimframes[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global gold
        self.count += 1
        if pygame.sprite.collide_mask(self, player):
            if self.rect.x > player.rect.x + player.rect.w:
                player.image = player.eatframes[0]
                player.image = player.eatframes[1]
            elif self.rect.x < player.rect.x:
                player.image = pygame.transform.flip(player.eatframes[0], 90, 0)
                player.image = pygame.transform.flip(player.eatframes[1], 90, 0)
            else:
                if player.mov <= 4:
                    player.image = player.eatframes[0]
                    player.image = player.eatframes[1]
                else:
                    player.image = pygame.transform.flip(player.eatframes[0], 90, 0)
                    player.image = pygame.transform.flip(player.eatframes[1], 90, 0)
            self.kill()
            gold += 1
            for i in range(len(player.swimframes)):
                player.swimframes[i] = pygame.transform.smoothscale(player.swimframes[i],
                                                                    (player.swimframes[i].get_width(),
                                                                     player.swimframes[i].get_height()))

        if self.count == 20:
            self.cur_frame = (self.cur_frame + 1) % len(self.swimframes)
            if self.swimstyle[0] < 0:
                self.image = pygame.transform.flip(self.swimframes[self.cur_frame], 90, 0)
            else:
                self.image = self.swimframes[self.cur_frame]
            self.count = 0

        S = (((player.rect.x + player.rect.w // 2) - (self.rect.x + self.rect.w // 2)) ** 2
             + ((player.rect.y + player.rect.h // 2) - (self.rect.y + self.rect.h // 2)) ** 2) ** 0.5
        if S <= 200 and self.swimstyle[1] == 0:
            self.swimstyle = [random.randint(-1, 1), random.randint(-1, 1)]
        if S >= 500 and self.swimstyle[1] != 0:
            self.swimstyle = [random.randint(-1, 1), 0]

        self.rect.x += self.swimstyle[0]
        self.rect.y += self.swimstyle[1]


class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__(all_sprites)
        self.add(plants)
        self.cur_frame = 0
        self.image = load_image(f'underwater_plants ({type}).png', -1)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, height - self.rect.h)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.y += self.dy
        obj.rect.x += self.dx

    # позиционировать камеру на объекте target
    def update(self, target):
        if player_pos[1] < 370:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
            self.dy = 0
        else:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def main():
    global player_pos
    global gold
    global file
    file = open('stat_datas').read()
    file = file.split('\n')
    gold = int(file[0])
    running = True
    FPS = 100
    motion = 'STOP'
    Sharky(width // 2 - 103, height // 2 - 42)
    camera.update(player)
    for i in range(100, -100, -1):
        Plant(i * 40, 0, random.randint(1, 9))
    speed = player.speedlevel + 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dats_write()
                running = False
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if motion == 'UP':
                        motion = 'LEFTUP'
                    elif motion == 'DOWN':
                        motion = 'LEFTDOWN'
                    else:
                        motion = 'LEFT'

                elif event.key == pygame.K_RIGHT:
                    if motion == 'UP':
                        motion = 'RIGHTUP'
                    elif motion == 'DOWN':
                        motion = 'RIGHTDOWN'
                    else:
                        motion = 'RIGHT'

                elif event.key == pygame.K_UP:
                    if motion == 'LEFT':
                        motion = 'LEFTUP'
                    elif motion == 'RIGHT':
                        motion = 'RIGHTUP'
                    else:
                        motion = 'UP'

                elif event.key == pygame.K_DOWN:
                    if motion == 'LEFT':
                        motion = 'LEFTDOWN'
                    elif motion == 'RIGHT':
                        motion = 'RIGHTDOWN'
                    else:
                        motion = 'DOWN'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Fish(event.pos[0], event.pos[1], 'yellowfish')
                elif event.button == 2:
                    Fish(event.pos[0], event.pos[1], 'goldfish')

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    if motion == 'LEFT':
                        motion = 'STOP'
                    elif motion == 'LEFTDOWN':
                        motion = 'DOWN'
                    elif motion == 'LEFTUP':
                        motion = 'UP'
                    else:
                        pass
                elif event.key == pygame.K_RIGHT:
                    if motion == 'RIGHT':
                        motion = 'STOP'
                    elif motion == 'RIGHTDOWN':
                        motion = 'DOWN'
                    elif motion == 'RIGHTUP':
                        motion = 'UP'
                    else:
                        pass
                elif event.key == pygame.K_UP:
                    if motion == 'UP':
                        motion = 'STOP'
                    elif motion == 'RIGHTUP':
                        motion = 'RIGHT'
                    elif motion == 'LEFTUP':
                        motion = 'LEFT'
                    else:
                        pass
                elif event.key == pygame.K_DOWN:
                    if motion == 'DOWN':
                        motion = 'STOP'
                    elif motion == 'RIGHTDOWN':
                        motion = 'RIGHT'
                    elif motion == 'LEFTDOWN':
                        motion = 'LEFT'
                    else:
                        pass

        if motion == 'LEFT':
            if player.mov < 9:
                player.movement(-1)
            else:
                player.rect.x -= speed
                player_pos = (player_pos[0] - speed, player_pos[1])
                camera.update(player)
                player.move()

        elif motion == 'RIGHT':
            if player.mov > 0:
                player.movement(1)
            else:
                player.rect.x += speed
                player_pos = (player_pos[0] + speed, player_pos[1])
                camera.update(player)
                player.move()

        elif motion == 'DOWN' and player_pos[1] > 60:
            player.rect.y += speed
            player_pos = (player_pos[0], player_pos[1] - speed)
            if player_pos[1] < 370:
                pass
            else:
                camera.update(player)
                player.move()

        elif motion == 'UP':
            player.rect.y -= speed
            player_pos = (player_pos[0], player_pos[1] + speed)
            if player_pos[1] < 370:
                pass
            else:
                camera.update(player)
                player.move()

        elif motion == 'RIGHTUP':
            if player.mov > 0:
                player.movement(1)
            else:
                player.rect.x += speed
                player.rect.y -= speed
                player_pos = (player_pos[0] + speed, player_pos[1] + speed)
                camera.update(player)
                player.move()
        elif motion == 'RIGHTDOWN':
            if player.mov > 0:
                player.movement(1)
            else:
                player.rect.x += speed
                player.rect.y += speed
                player_pos = (player_pos[0] + speed, player_pos[1] - speed)
                camera.update(player)
                player.move()
        elif motion == 'LEFTUP':
            if player.mov < 9:
                player.movement(-1)
            else:
                player.rect.x -= speed
                player.rect.y -= speed
                player_pos = (player_pos[0] - speed, player_pos[1] + speed)
                camera.update(player)
                player.move()
        elif motion == 'LEFTDOWN':
            if player.mov < 9:
                player.movement(-1)
            else:
                player.rect.x -= speed
                player.rect.y += speed
                player_pos = (player_pos[0] - speed, player_pos[1] - speed)
                camera.update(player)
                player.move()

        screen.fill((0, 0, 255))
        screen.blit(fon, (0, 0))
        screen.blit(monet, (990, 10))
        font = pygame.font.Font(None, 60)
        text = font.render(f"{gold}", 1, (0, 0, 0))
        screen.blit(text, (1000 - len(str(gold)) * 30, 15))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(320, 50, 400, 20), 1)
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(320, 50, 400 * (player.health / player.maxhealth), 20))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(320 + 400 * (player.health / player.maxhealth), 50,
                                                          400 - 400 * (player.health / player.maxhealth) + 5, 20))
        if player.health == 0:
            again = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((400, 365), (280, 50)))
            menu = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((400, 425), (280, 50)))
            screen.blit(pygame.transform.scale(button, (350, 90)), (360, 350))
            screen.blit(pygame.transform.scale(button, (350, 90)), (360, 410))
            text = font.render(f"AGAIN", 1, (0, 0, 0))
            screen.blit(text, (475, 370))
            text = font.render(f"MENU", 1, (0, 0, 0))
            screen.blit(text, (485, 430))
            dats_write()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if again.collidepoint(event.pos):
                            main()
                        elif menu.collidepoint(event.pos):
                            start_screen()

        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    global gold
    global file
    file = open('stat_datas').read()
    file = file.split('\n')
    gold = int(file[0])
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 60)
    play = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((500, 20), (140, 50)))
    screen.blit(pygame.transform.scale(load_image('button.png', -1), (175, 90)), (480, 5))
    text = font.render(f"PLAY", 1, (0, 0, 0))
    screen.blit(text, (520, 25))
    upgrades = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((430, 75), (280, 50)))
    screen.blit(pygame.transform.scale(load_image('button.png', -1), (350, 90)), (390, 60))
    text = font.render(f"UPGRADES", 1, (0, 0, 0))
    screen.blit(text, (450, 80))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and play.collidepoint(event.pos):
                main()  # начинаем игру
            elif event.type == pygame.MOUSEBUTTONDOWN and upgrades.collidepoint(event.pos):
                fon = pygame.transform.scale(load_image('upg_fon.jpg'), (width, height))
                Sharky(450, 200)
                while True:
                    screen.blit(fon, (0, 0))
                    all_sprites.draw(screen)
                    all_sprites.update()
                    speeed = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((88, 514), (255, 50)))
                    health = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((430, 514), (280, 50)))
                    back = pygame.draw.rect(screen, (168, 168, 168), pygame.Rect((20, 20), (140, 50)))
                    screen.blit(pygame.transform.scale(button, (350, 90)), (390, 500))
                    screen.blit(pygame.transform.scale(button, (350, 90)), (50, 500))
                    screen.blit(pygame.transform.scale(button, (175, 90)), (0, 6))
                    text = font.render(f"UPGRADES", 1, (0, 0, 0))
                    screen.blit(text, (450, 80))
                    text = font.render(f"SPEED", 1, (0, 0, 0))
                    screen.blit(text, (150, 450))
                    text = font.render(f"HEALTH", 1, (0, 0, 0))
                    screen.blit(text, (480, 450))
                    text = font.render(f"BACK", 1, (0, 0, 0))
                    screen.blit(text, (30, 30))
                    if player.speedlevel == 5:
                        text = font.render(f"MAX", 1, (0, 0, 0))
                    else:
                        text = font.render(f"{speedups[player.speedlevel]}", 1, (0, 0, 0))
                        screen.blit(monet, (260, 515))
                    screen.blit(text, (170, 519))
                    if player.maxhealth == 60000:
                        text = font.render(f"MAX", 1, (0, 0, 0))
                    else:
                        text = font.render(f"{healthups[int(player.maxhealth / 10000) - 1]}", 1, (0, 0, 0))
                        screen.blit(monet, (600, 515))
                    screen.blit(text, (510, 519))
                    screen.blit(monet, (980, 10))
                    font = pygame.font.Font(None, 60)
                    text = font.render(f"{gold}", 1, (0, 0, 0))
                    screen.blit(text, (1000 - len(str(gold)) * 30, 15))

                    pygame.display.flip()
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            dats_write()
                            terminate()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if speeed.collidepoint(event.pos):
                                    if player.speedlevel == 5:
                                        pass
                                    else:
                                        gold -= speedups[player.speedlevel]
                                        player.speedlevel += 1
                                elif back.collidepoint(event.pos):
                                    dats_write()
                                    start_screen()

                                elif health.collidepoint(event.pos):
                                    if player.maxhealth == 60000:
                                        pass
                                    else:
                                        gold -= healthups[int(player.maxhealth / 10000) - 1]
                                        player.maxhealth += 10000

        pygame.display.flip()


camera = Camera()
file = open('stat_datas').read()
file = file.split('\n')
start_screen()

if __name__ == '__main__':
    main()
