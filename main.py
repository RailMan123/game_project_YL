import pygame
import os
import time

pygame.init()
size = width, height = 1000, 700
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))
all_sprites = pygame.sprite.Group()
fishes = pygame.sprite.Group()
shark = pygame.sprite.Group()
ontime = 0
running = True
clock = pygame.time.Clock()
speed = 10


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
        super().__init__(all_sprites)
        self.swimframes = []
        self.moveframes = []
        self.eatframes = []
        self.rect = pygame.Rect((0, 0), (207, 85))
        for i in range(1, 6):
            sheet = load_image(f'bluesharkswim(' + str(i) + ').png', colorkey=-1)
            self.swimframes.append(sheet.subsurface(pygame.Rect(
                (0, 0), sheet.get_rect().size)))
        for i in range(1, 11):
            sheet = load_image(f'bluesharkmove' + str(i) + '.png', colorkey=-1)
            self.moveframes.append(sheet.subsurface(pygame.Rect(
                (0, 0), sheet.get_rect().size)))
        cut_sheet(self, load_image('bluesharkeat.png', colorkey=-1), 2, 1, self.eatframes)
        self.add(shark)
        self.cur_frame = 0
        self.image = self.swimframes[self.cur_frame]
        self.rect = self.rect.move(x, y)
        player = self
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.mov = 0

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
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(fishes)
        self.swimframes = []
        cut_sheet(self, load_image('yellowfishswim.png', colorkey=-1), 6, 1, self.swimframes)
        self.cur_frame = 0
        self.image = self.swimframes[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.count += 1
        if pygame.sprite.collide_mask(self, player):
            if player.mov <= 4:
                player.image = player.eatframes[0]
                player.image = player.eatframes[1]
            else:
                player.image = pygame.transform.flip(player.eatframes[0], 90, 0)
                player.image = pygame.transform.flip(player.eatframes[1], 90, 0)
            self.kill()
            for i in range(len(player.swimframes)):
                player.swimframes[i] = pygame.transform.smoothscale(player.swimframes[i],
                                                                    (player.swimframes[i].get_width(),
                                                                     player.swimframes[i].get_height()))

        if self.count == 20:
            self.cur_frame = (self.cur_frame + 1) % len(self.swimframes)
            self.image = self.swimframes[self.cur_frame]
            self.count = 0


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
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


speed = 100
motion = 'STOP'
Sharky(200, 200)
direct = 1
camera = Camera()
camera.update(player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                motion = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                motion = 'RIGHT'
            elif event.key == pygame.K_UP:
                motion = 'UP'
            elif event.key == pygame.K_DOWN:
                motion = 'DOWN'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            Fish(event.pos[0], event.pos[1])
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                motion = 'STOP'

    if motion == 'LEFT':
        if player.mov < 9:
            player.movement(-1)
        else:
            player.rect.x -= 3
            camera.update(player)
            player.move()
    elif motion == 'RIGHT':
        if player.mov > 0:
            player.movement(1)
        else:
            player.rect.x += 3
            camera.update(player)
            player.move()
    elif motion == 'DOWN':
        player.rect.y += 3
        camera.update(player)
        player.move()
    elif motion == 'UP':
        player.rect.y -= 3
        camera.update(player)
        player.move()

    screen.blit(fon, (0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(speed)
