import pygame
import os
import time
import random
import sys

pygame.init()
size = width, height = 1050, 750
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
screen.fill((0, 0, 255))
ontime = 0
running = True
clock = pygame.time.Clock()
speed = 10
plants_row = (0, 1000)
player_pos = ()


def terminate():
    pygame.quit()
    sys.exit()


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


fon = pygame.transform.scale(load_image('background.jpg'), (width, height))
screen.blit(fon, (0, 0))
screen.blit(load_image('underwater_plants (1).png'), (0, 0))


def cut_sheet(self, sheet, columns, rows, frames):
    self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))


player = 0


class Sharky(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global player
        global player_pos
        super().__init__(all_sprites)
        self.swimframes = []
        self.moveframes = []
        self.eatframes = []
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
        player = self
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.mov = 0
        player_pos = (player.rect.x + player.rect.w // 2, player.rect.y + player.rect.h // 2)

    def update(self):
        self.count += 1
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


all_sprites = pygame.sprite.Group()
fishes = pygame.sprite.Group()
plants = pygame.sprite.Group()
FPS = 100
motion = 'STOP'
Sharky(width // 2 - 103, height // 2 - 42)
direct = 1
camera = Camera()
camera.update(player)
for i in range(100, -100, -1):
    Plant(i * 40, 0, random.randint(1, 9))
monet = load_image('monet.png', -1)
monet = pygame.transform.scale(monet, (50, 50))
gold = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
            player.rect.x -= 3
            player_pos = (player_pos[0] - 3, player_pos[1])
            camera.update(player)
            player.move()

    elif motion == 'RIGHT':
        if player.mov > 0:
            player.movement(1)
        else:
            player.rect.x += 3
            player_pos = (player_pos[0] + 3, player_pos[1])
            camera.update(player)
            player.move()

    elif motion == 'DOWN' and player_pos[1] > 60:
        player.rect.y += 3
        player_pos = (player_pos[0], player_pos[1] - 3)
        if player_pos[1] < 370:
            pass
        else:
            camera.update(player)
            player.move()

    elif motion == 'UP':
        player.rect.y -= 3
        player_pos = (player_pos[0], player_pos[1] + 3)
        if player_pos[1] < 370:
            pass
        else:
            camera.update(player)
            player.move()

    elif motion == 'RIGHTUP':
        if player.mov > 0:
            player.movement(1)
        else:
            player.rect.x += 2
            player.rect.y -= 2
            player_pos = (player_pos[0] + 2, player_pos[1] + 2)
            camera.update(player)
            player.move()
    elif motion == 'RIGHTDOWN':
        if player.mov > 0:
            player.movement(1)
        else:
            player.rect.x += 2
            player.rect.y += 2
            player_pos = (player_pos[0] + 2, player_pos[1] - 2)
            camera.update(player)
            player.move()
    elif motion == 'LEFTUP':
        if player.mov < 9:
            player.movement(-1)
        else:
            player.rect.x -= 2
            player.rect.y -= 2
            player_pos = (player_pos[0] - 2, player_pos[1] + 2)
            camera.update(player)
            player.move()
    elif motion == 'LEFTDOWN':
        if player.mov < 9:
            player.movement(-1)
        else:
            player.rect.x -= 2
            player.rect.y += 2
            player_pos = (player_pos[0] - 2, player_pos[1] - 2)
            camera.update(player)
            player.move()

    screen.fill((0, 0, 255))
    screen.blit(fon, (0, 0))
    screen.blit(monet, (990, 10))
    font = pygame.font.Font(None, 70)
    text = font.render(f"{gold}", 1, (255, 255, 0))
    screen.blit(text, (1000 - len(str(gold)) * 30, 10))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
