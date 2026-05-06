import pygame as pg

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(size=(1280, 640))

def get_img(name, mirrored_x, mirrored_y):
    return pg.transform.flip(pg.transform.scale(pg.image.load(f'Sprites/{name}'),
                        (32, 32)), flip_x=mirrored_x,
                             flip_y=mirrored_y)


"""
Загрузка и подготовка всех спрайтов персонажа.
Для каждого состояния (idle, walk, jump, fall) создаются версии 
для правого (0) и левого (1) направлений движения.
"""
idle1_r = get_img('player_idle1.png', False, False)
idle2_r = get_img('player_idle2.png', False, False)
idle1_l = get_img('player_idle1.png', True, False)
idle2_l = get_img('player_idle2.png', True, False)
walk1_r = get_img('player_walk1.png', False, False)
walk2_r = get_img('player_walk2.png', False, False)
walk1_l = get_img('player_walk1.png', True, False)
walk2_l = get_img('player_walk2.png', True, False)
jump_r = get_img('player_jump.png', False, False)
fall_r = get_img('player_fall.png', False, False)
jump_l = get_img('player_jump.png', True, False)
fall_l = get_img('player_fall.png', True, False)

"""
Словарь для организации всех спрайтов персонажа.
Структура: состояние -> направление -> список кадров анимации.
Направление 0 = вправо, 1 = влево.
"""
player_dict = {
    'idle': {0: [idle1_r, idle2_r],
             1: [idle1_l, idle2_l]},
    'walk': {0: [walk1_r, walk2_r],
             1: [walk1_l, walk2_l]},
    'jump': {0: [jump_r],
             1: [jump_l]},
    'fall': {0: [fall_r],
             1: [fall_l]}
}

"""
Списки для хранения спрайтов различных типов стен и шипов.
Каждый индекс соответствует определенному повороту спрайта.
"""
wall = []
corner_wall = []
inner_corner_wall = []
spikes = []

"""
Загрузка спрайтов стен с различными поворотами (0, 90, 180, 270 градусов).
Также загружается спрайт пустой стены для заполнения внутренних областей.
"""
wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/wall.png'), 0), (32, 32)))
wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/wall.png'), 90), (32, 32)))
wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/wall.png'), 180), (32, 32)))
wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/wall.png'), 270), (32, 32)))
wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/empty_wall.png'), 0), (32, 32)))

"""
Загрузка спрайтов для наружных углов стен с четырьмя вариантами поворота.
"""
corner_wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/corner_wall.png'), 0), (32, 32)))
corner_wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/corner_wall.png'), 90), (32, 32)))
corner_wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/corner_wall.png'), 180), (32, 32)))
corner_wall.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/corner_wall.png'), 270), (32, 32)))

"""
Загрузка спрайтов для внутренних углов стен с четырьмя вариантами поворота.
"""
inner_corner_wall.append(
    pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/inner_corner_wall.png'), 0), (32, 32)))
inner_corner_wall.append(
    pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/inner_corner_wall.png'), 90), (32, 32)))
inner_corner_wall.append(
    pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/inner_corner_wall.png'), 180), (32, 32)))
inner_corner_wall.append(
    pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/inner_corner_wall.png'), 270), (32, 32)))

"""
Загрузка спрайтов шипов с поворотами 0 (вверх) и 180 (вниз) градусов.
Шипы имеют высоту 16 пикселей (половина стандартного размера клетки).
"""
spikes.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/spikes.png'), 0), (32, 16)))
spikes.append(pg.transform.scale(pg.transform.rotate(pg.image.load('Sprites/spikes.png'), 180), (32, 16)))

"""
Словарь соответствия символов карты и игровых объектов.
Используются псевдографические символы для визуального редактирования уровней.
"""
symb_dict = {
    '•': None,
    'S': None,
    'F': None,
    '▀': wall[0],
    '▌': wall[1],
    '▄': wall[2],
    '▐': wall[3],
    '█': wall[4],
    '▜': corner_wall[0],
    '▛': corner_wall[1],
    '▙': corner_wall[2],
    '▟': corner_wall[3],
    '▝': inner_corner_wall[0],
    '▘': inner_corner_wall[1],
    '▖': inner_corner_wall[2],
    '▗': inner_corner_wall[3],
    '▲': spikes[0],
    '▼': spikes[1],
}

"""
Загрузка карты уровня из текстового файла.
Каждая строка файла преобразуется в список символов.
"""
map_list = []
with open('level_map.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line_list = list(line.strip())
        map_list.append(line_list)


class Player:
    def __init__(self, x, y):
        self.states = {
            'standing': False
        }
        self.direction = 0  # 0 = вправо, 1 = влево
        self.vel_y = 0  # вертикальная скорость
        self.vel_x = 0  # горизонтальная скорость
        self.gravity = 0.5  # сила гравитации
        self.hitbox_size = (24, 32)  # размер хитбокса (меньше спрайта)
        self.rect = pg.Rect((x, y, self.hitbox_size[0], self.hitbox_size[1]))
        self.current_img = player_dict['idle'][0][0]  # текущий спрайт
        self.img_offset = 0  # смещение спрайта относительно хитбокса
        self.jumps_left = 2  # оставшиеся прыжки (для двойного прыжка)

        self.anim_timer = 0  # таймер анимации
        self.anim_frame = 0  # текущий кадр анимации
        self.anim_speed = 15  # скорость смены кадров (в кадрах игры)

    def set_img(self, key, direction, index):
        self.current_img = player_dict[key][direction][index]
        self.direction = direction
        if direction == 1:
            self.img_offset = -(self.current_img.get_width() - self.hitbox_size[0])
        else:
            self.img_offset = 0

    def update_animation(self):
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            # Определение максимального количества кадров для текущего состояния
            if self.vel_y < 0:  # прыжок
                max_frames = len(player_dict['jump'][self.direction])
            elif self.vel_y > 0:  # падение
                max_frames = len(player_dict['fall'][self.direction])
            elif self.vel_x != 0:  # ходьба
                max_frames = len(player_dict['walk'][self.direction])
            else:  # покой
                max_frames = len(player_dict['idle'][self.direction])

            # Переключение на следующий кадр с циклическим возвратом
            self.anim_frame = (self.anim_frame + 1) % max_frames
            # Обновление спрайта с учетом текущего состояния
            if self.vel_y < 0:
                self.set_img('jump', self.direction, self.anim_frame)
            elif self.vel_y > 0:
                self.set_img('fall', self.direction, self.anim_frame)
            elif self.vel_x != 0:
                self.set_img('walk', self.direction, self.anim_frame)
            else:
                self.set_img('idle', self.direction, self.anim_frame)

    def draw(self):
        screen.blit(self.current_img, (self.rect.x + self.img_offset, self.rect.y))

    def jump(self, power):
        if self.states['standing']:
            self.vel_y = power
            self.states['standing'] = False
            self.jumps_left = 1
        elif self.jumps_left > 0:
            self.vel_y = power
            self.jumps_left -= 1

    def move_y(self):
        if not self.states['standing']:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

    def move_x(self):
        self.rect.centerx += self.vel_x

    def check_spikes_collision(self, spikes):
        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                self.rect.x, self.rect.y = start_pos

    def check_finish(self, finish_rect):
        if self.rect.colliderect(finish_rect):
            self.rect.x, self.rect.y = start_pos

    def collision_move_update(self, solids):
        was_standing = self.states['standing']
        self.states['standing'] = False
        self.move_y()
        self.move_x()

        for obj in solids:
            if (self.vel_y > 0 and
                    self.rect.right > obj.rect.left and self.rect.left < obj.rect.right and
                    obj.rect.top + 10 >= self.rect.bottom >= obj.rect.top and
                    self.rect.top <= obj.rect.bottom):
                self.rect.bottom, self.vel_y, self.states['standing'] = obj.rect.top, 0, True
            elif (self.vel_y < 0 and
                  self.rect.right > obj.rect.left and self.rect.left < obj.rect.right and
                  obj.rect.bottom - 10 <= self.rect.top <= obj.rect.bottom and
                  self.rect.bottom >= obj.rect.top):
                self.rect.top, self.vel_y = obj.rect.bottom, 0
            if (self.vel_x > 0 and
                    self.rect.right > obj.rect.left and self.rect.left < obj.rect.right and
                    self.rect.top < obj.rect.bottom and
                    self.rect.bottom > obj.rect.top):
                self.rect.right = obj.rect.left
            elif (self.vel_x < 0 and
                  self.rect.left < obj.rect.right and
                  self.rect.right > obj.rect.left and
                  self.rect.top < obj.rect.bottom and
                  self.rect.bottom > obj.rect.top):
                self.rect.left = obj.rect.right
        if self.states['standing'] and not was_standing:
            self.jumps_left = 2
        if not self.states['standing'] and was_standing:
            self.jumps_left = 1


"""
Глобальный список всех шипов на уровне.
Используется для проверки столкновений с персонажем.
"""
all_spikes = []


class Spike:
    """
    Класс опасных объектов (шипов).
    При касании возвращает персонажа на начальную позицию.
    """

    def __init__(self, x, y, img):
        """
        Создание шипа в заданной позиции.

        Параметры:
            x: координата X
            y: координата Y
            img: спрайт шипа
        """
        self.x = x
        self.y = y
        self.img = img
        self.rect = pg.Rect(x, y, 32, 16)  # хитбокс половинной высоты
        all_spikes.append(self)

    def draw(self):
        """
        Отрисовка шипа на экране.
        """
        screen.blit(self.img, self.rect)


"""
Глобальный список всех твердых объектов (стен и платформ).
Используется для проверки столкновений и отрисовки.
"""
all_solids = []


class Solid:
    """
    Класс твердых статических объектов (стены, платформы).
    Формируют игровое пространство уровня.
    """

    def __init__(self, x, y, height, width, img, debug):
        """
        Создание твердого объекта.

        Параметры:
            x: координата X
            y: координата Y
            height: высота
            width: ширина
            img: спрайт объекта
            debug: символ для отладки (тип стены)
        """
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.rect = pg.Rect(x, y, width, height)
        self.img = img
        all_solids.append(self)

    def draw(self):
        """
        Отрисовка твердого объекта на экране.
        """
        screen.blit(self.img, self.rect)


"""
Список прямоугольников финишных зон.
Может содержать несколько зон финиша на одном уровне.
"""
finish_rects = []

"""
Кортеж с начальной позицией персонажа.
Обновляется при обработке карты уровня.
"""
start_pos = (0, 0)

"""
Обработка карты уровня: создание игровых объектов на основе символов.
Каждый символ преобразуется в соответствующий игровой объект
с позиционированием по сетке 32x32 пикселя.
"""
current_row = -1
for line in map_list:
    current_row += 1
    current_column = -1
    for symbol in line:
        current_column += 1
        picture = symb_dict[f'{symbol}']
        if picture:
            # Создание стен и углов
            if symbol in ['█', '▀', '▌', '▄', '▐', '▜', '▛', '▙', '▟', '▝', '▘', '▖', '▗']:
                new_cell = Solid(current_column * 32, current_row * 32, 32, 32, picture, symbol)
            # Создание шипов направленных вверх
            elif symbol in ['▲']:
                new_cell = Spike(current_column * 32, current_row * 32 + 16, picture)
            # Создание шипов направленных вниз
            elif symbol in ['▼']:
                new_cell = Spike(current_column * 32, current_row * 32, picture)
        else:
            # Пустое пространство
            if symbol == '•':
                pass
            # Стартовая позиция персонажа
            elif symbol == 'S':
                start_pos = (current_column * 32, current_row * 32)
            # Финишная зона
            elif symbol == 'F':
                finish_rect = pg.Rect(current_column * 32, current_row * 32, 32, 32)
                finish_rects.append(finish_rect)

"""
Создание экземпляра игрока на стартовой позиции.
"""
player = Player(start_pos[0], start_pos[1])

"""
Словарь для отслеживания состояния клавиш движения.
"""
ad_pressed = {'a': False, 'd': False}

"""
Основной игровой цикл.
Обрабатывает события, обновляет состояние игры и отрисовывает кадры.
"""
running = True
while running:
    clock.tick(60)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if player.states['standing']:
                    player.jump(-8)
                else:
                    player.jump(-7)
            if event.key == pg.K_a:
                ad_pressed['a'] = True
            if event.key == pg.K_d:
                ad_pressed['d'] = True
            if event.key == pg.K_r:
                player.rect.x, player.rect.y = start_pos
        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                ad_pressed['a'] = False
            if event.key == pg.K_d:
                ad_pressed['d'] = False
    if ad_pressed['a'] and not ad_pressed['d']:
        player.vel_x = -4
        player.direction = 1
    elif ad_pressed['d'] and not ad_pressed['a']:
        player.vel_x = 4
        player.direction = 0
    else:
        player.vel_x = 0

    # Обновление физики и проверка столкновений
    player.collision_move_update(all_solids)
    player.check_spikes_collision(all_spikes)

    # Проверка падения за пределы уровня (смерть)
    if player.rect.bottom > 1000:
        player.rect.x, player.rect.y = start_pos
        player.vel_y = 0

    # Очистка экрана (темно-синий фон)
    screen.fill((1, 1, 10))

    # Обновление анимации персонажа (цикл анимации)
    player.update_animation()

    # Отрисовка всех игровых объектов
    player.draw()
    for solid in all_solids:
        solid.draw()
    for spike in all_spikes:
        spike.draw()
    for f in finish_rects:
        pg.draw.rect(screen, (0, 255, 0), f)  # Зеленый цвет финиша
        player.check_finish(f)

    # Обновление экрана
    pg.display.flip()

# Завершение работы Pygame
pg.quit()