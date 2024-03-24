import pygame
import pygame_gui
import os
import sys
import random
from maps import maze_generator

WINDOWS_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 950, 800
FPS = 15
MAPS_DIR = "maps"
TITLE_SIZE = 32
ENEMY_EVENT_TYPE = pygame.USEREVENT + 1
DELAY = 150
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Labyrinth:

    def __init__(self, filename, free_tiles, finish_tile, level_tile):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = TITLE_SIZE
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile
        self.level_tile = level_tile

    def render(self, screen):
        tile_images = {
            0: load_image("floor.png"),  # Изображение для пустой клетки
            1: load_image("wall.png"),  # Изображение для стены
            2: load_image("exit.png"),  # Изображение для стены
            3: load_image("wall.png"),  # Изображение для стены
            4: load_image("finish.png"),  # Изображение для стены
        }

        for y in range(self.height):
            for x in range(self.width):
                tile_image = tile_images[self.get_tile_id((x, y))]
                screen.blit(tile_image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and \
                        self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def generate_coins(self, num_coins):
        free_positions = [(x, y) for y in range(self.height - 1) for x in range(self.width - 1) if self.is_free((x, y))]
        return random.sample(free_positions, num_coins)

    def update_from_file(self, filename):
        with open(filename) as input_file:
            self.map = []
            for line in input_file:
                self.map.append(list(map(int, line.split())))


class Hero:

    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        tile_image = load_image("hero1.png")
        center = self.x * TITLE_SIZE + TITLE_SIZE // 2 - 32, self.y * TITLE_SIZE + TITLE_SIZE // 2 - 42
        screen.blit(tile_image, center)


class Enemy:

    def __init__(self, position):
        self.x, self.y = position
        self.delay = 0
        self.paused = False
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def get_delay(self):
        return self.delay

    def set_delay(self, de):
        self.delay = de
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def render(self, screen):
        tile_image = load_image("enemy1.png")
        center = self.x * TITLE_SIZE + TITLE_SIZE // 2 - 32, self.y * TITLE_SIZE + TITLE_SIZE // 2 - 42
        screen.blit(tile_image, center)


class Coin(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.x, self.y = position
        self.is_collected = False
        self.image = pygame.Surface((TITLE_SIZE // 2, TITLE_SIZE // 2))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(self.x * TITLE_SIZE + TITLE_SIZE // 2 - 20,
                                                self.y * TITLE_SIZE + TITLE_SIZE // 2 - 20))

    def render(self, screen):
        tile_image = load_image("coin1.png")
        screen.blit(tile_image, self.rect)

    def get_position(self):
        return self.x, self.y


def find_exit_coordinates(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    for y, line in enumerate(lines):
        for x, char in enumerate(line.split()):
            if char == '2':
                return x, y


def update_exit_to_wall(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines2 = []
    for line in lines:
        line2 = line.replace("2", "3")
        lines2.append(line2)

    with open(filename, 'w') as f:
        f.writelines(lines2)


def get_random_free_coordinate(is_free_function):
    while True:
        x1 = random.randint(0, 23)
        y1 = random.randint(0, 23)
        if is_free_function((x1, y1)):
            for _ in range(100):
                dx = random.randint(-10, 10)
                dy = random.randint(-10, 10)
                if abs(dx) + abs(dy) == 20:
                    x2 = x1 + dx
                    y2 = y1 + dy
                    if 0 <= x2 <= 23 and 0 <= y2 <= 23 and is_free_function((x2, y2)):
                        return (x1, y1), (x2, y2)


def update_wall_to_exit(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines2 = []
    for line in lines:
        line2 = line.replace("3", "2")
        lines2.append(line2)

    with open(filename, 'w') as f:
        f.writelines(lines2)


def update_wall_to_win(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines2 = []
    for line in lines:
        line2 = line.replace("3", "4")
        lines2.append(line2)

    with open(filename, 'w') as f:
        f.writelines(lines2)


class Game:

    def __init__(self, labyrinth, hero, enemy, coins):
        self.labyrinth = labyrinth
        self.hero = hero
        self.enemy = enemy
        self.coins = coins
        self.collected_coins = 0
        self.level_coins = 0
        self.is_paused = False
        self.short_sound_allowed = True
        self.exit_coordinates = find_exit_coordinates('maps/map.txt')
        update_exit_to_wall('maps/map.txt')
        self.levels = 3
        self.state = {
            'hero_position': hero.get_position(),
            'enemy_position': enemy.get_position(),
            'collected_coins': self.get_collected_coins(),
            'enemy_delay': enemy.get_delay(),
            'levels': self.get_levels(),
            'level_coins': self.get_level_coins()
        }

    def get_short_sound_allowed(self):
        return self.short_sound_allowed

    def set_short_sound_allowed(self, so):
        self.short_sound_allowed = so

    def get_collected_coins(self):
        return self.collected_coins

    def set_collected_coins(self, co):
        self.collected_coins = co

    def get_level_coins(self):
        return self.level_coins

    def set_level_coins(self, co):
        self.level_coins = co

    def get_levels(self):
        return self.levels

    def set_levels(self, le):
        self.levels = le

    def save_game(self, filename, omap, savemap):
        with open(filename, 'w') as f:
            f.write(f"{self.state['hero_position'][0]} {self.state['hero_position'][1]}\n")
            f.write(f"{self.state['enemy_position'][0]} {self.state['enemy_position'][1]}\n")
            f.write(f"{self.state['collected_coins']}\n")  # Сохраняем количество собранных монеток
            f.write(f"{self.state['enemy_delay']}\n")
            f.write(f"{self.state['levels']}\n")
            f.write(f"{self.state['level_coins']}\n")
            for coin in self.coins:
                f.write(f"{coin.get_position()[0]} {coin.get_position()[1]} {coin.is_collected}\n")
        with open(omap, 'r') as f:
            lines = f.readlines()
        with open(savemap, 'w') as f:
            f.writelines(lines)

    def load_game(self, filename, omap, savemap):
        with open(filename, 'r') as f:
            hero_x, hero_y = map(int, f.readline().split())
            enemy_x, enemy_y = map(int, f.readline().split())
            self.state['hero_position'] = (hero_x, hero_y)
            self.state['enemy_position'] = (enemy_x, enemy_y)
            self.hero.set_position(self.state['hero_position'])
            self.enemy.set_position(self.state['enemy_position'])
            co = int(f.readline())
            self.set_collected_coins(co)
            de = int(f.readline())
            self.enemy.set_delay(de)
            le = int(f.readline())
            self.set_levels(le)
            lco = int(f.readline())
            self.set_level_coins(lco)

            coin_data = [line.split() for line in f.readlines()]
            coin_positions = [(int(data[0]), int(data[1])) for data in coin_data]
            coin_collected = [data[2] == 'True' for data in coin_data]
            self.coins = [Coin(pos) for pos in coin_positions]
            for coin, collected in zip(self.coins, coin_collected):
                coin.is_collected = collected

            with open(savemap, 'r') as fr:
                lines = fr.readlines()
            with open(omap, 'w') as fw:
                fw.writelines(lines)

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)
        black_surface = pygame.Surface((390, 30), pygame.SRCALPHA)
        black_surface.fill((0, 0, 0, 128))
        screen.blit(black_surface, (0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {self.collected_coins} ', True, (255, 255, 255))
        text2 = font.render(f'level: {1 + 3 - self.levels} of 3', True, (255, 255, 255))
        screen.blit(text, (10, 2))
        screen.blit(text2, (230, 2))
        fontd = pygame.font.Font(None, 36)
        if self.enemy.get_delay() == 300:
            textd = fontd.render(f'Easy', True, (0, 255, 0))
            screen.blit(textd, (127, 2))
        elif self.enemy.get_delay() == 170:
            textd = fontd.render(f'Normal', True, (255, 255, 0))
            screen.blit(textd, (127, 2))
        elif self.enemy.get_delay() == 120:
            textd = fontd.render(f'Hard', True, (255, 0, 0))
            screen.blit(textd, (127, 2))
        for coin in self.coins:
            coin.render(screen)
        self.enemy.render(screen)

    def update_hero(self):
        self.state['enemy_delay'] = self.enemy.get_delay()
        self.state['hero_position'] = self.hero.get_position()
        self.state['collected_coins'] = self.get_collected_coins()
        self.state['levels'] = self.get_levels()
        self.state['level_coins'] = self.get_level_coins()
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))
        for coin in self.coins:
            if self.hero.get_position() == coin.get_position():
                self.coins.remove(coin)
                if self.short_sound_allowed is True:
                    sound1 = pygame.mixer.Sound("data/carrot.mp3")
                    sound1.set_volume(10)
                    sound1.play()
                self.collected_coins += 1
                self.level_coins += 1

    def move_enemy(self):
        if not self.enemy.paused:
            next_position = self.labyrinth.find_path_step(self.enemy.get_position(),
                                                          self.hero.get_position())
            self.enemy.set_position(next_position)
            self.state['enemy_position'] = next_position  # Обновляем позицию врага в состоянии игры

    def check_win(self):
        return self.labyrinth.get_tile_id(self.hero.get_position()) == self.labyrinth.finish_tile

    def check_level(self):
        return self.labyrinth.get_tile_id(self.hero.get_position()) == self.labyrinth.level_tile

    def check_lose(self):
        return self.hero.get_position() == self.enemy.get_position()

    def switch_pause(self):
        self.is_paused = not self.is_paused
        pygame.time.set_timer(ENEMY_EVENT_TYPE, DELAY if not self.is_paused else 0)
        self.enemy.paused = self.is_paused


class UI:
    def __init__(self, game):
        self.game = game

    def menu(self, manager):
        self.k_pause = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 30), (100, 50)),
            text='Пауза',
            manager=manager
        )
        self.k_restart = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 500), (100, 50)),
            text='Рестарт',
            manager=manager
        )
        self.k_save = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 630), (100, 50)),
            text='Сохранение',
            manager=manager
        )
        self.k_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 700), (100, 50)),
            text='Загрузка',
            manager=manager
        )
        self.k_diff = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 440), (100, 50)),
            text='Сложность',
            manager=manager
        )
        self.k_music = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 100), (100, 50)),
            text='Музыка',
            manager=manager
        )
        self.k_sound = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 150), (100, 50)),
            text='Звуки',
            manager=manager
        )

    def difficulty(self, manager):
        self.k_easy = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 200), (200, 50)),
            text='Легкий',
            manager=manager
        )
        self.k_normal = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 270), (200, 50)),
            text='Средний',
            manager=manager
        )
        self.k_hard = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 340), (200, 50)),
            text='Сложный',
            manager=manager
        )

        self.k_hint = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 450), (220, 50)),
            text='Открыть/закрыть правила',
            manager=manager
        )

    def save_game(self):
        self.game.save_game("save/save_game.txt", "maps/map.txt", "maps/savemap.txt")

    def load_game(self):
        self.game.load_game("save/save_game.txt", "maps/map.txt", "maps/savemap.txt")


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, ui, manager, game):
    ui.difficulty(manager)
    intro_text = ["Добро пожаловать в игру \"Ушастый Побег\"!",
                  "Чтобы начать играть, выберите",
                  "уровень сложности:"]

    fon = pygame.transform.scale(load_image('fon1.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 20
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        intro_rect.y += 20
        text_coord += intro_rect.height * 1.2
        screen.blit(string_rendered, intro_rect)
    time_delta = clock.tick(60) / 1000.0
    show_hint = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == ui.k_easy:
                        ui.k_easy.hide()
                        ui.k_normal.hide()
                        ui.k_hard.hide()
                        ui.k_hint.hide()
                        game.enemy.set_delay(300)
                        return()
                    elif event.ui_element == ui.k_normal:
                        ui.k_easy.hide()
                        ui.k_normal.hide()
                        ui.k_hard.hide()
                        ui.k_hint.hide()
                        game.enemy.set_delay(170)
                        return()
                    elif event.ui_element == ui.k_hard:
                        ui.k_easy.hide()
                        ui.k_normal.hide()
                        ui.k_hard.hide()
                        ui.k_hint.hide()
                        game.enemy.set_delay(120)
                        return()
                    elif event.ui_element == ui.k_hint:
                        if show_hint is False:
                            show_hint = True
                            black_surface = pygame.Surface((550, 150), pygame.SRCALPHA)
                            black_surface.fill((0, 0, 0, 200))
                            screen.blit(black_surface, (240, 300))
                            pygame.font.Font(None, 36)
                            hint_text = ["Помогите зайцу сбежать от волка!",
                                         "Чтобы открылся проход на следующий уровень,",
                                         "Соберите 5 морковок. Пройдите 3 уровня,",
                                         "Собрав как можно больше морковок!"]
                            font2 = pygame.font.Font(None, 30)
                            text_coord2 = 290
                            for line in hint_text:
                                string_rendered = font2.render(line, True, pygame.Color('white'))
                                hint_rect = string_rendered.get_rect()
                                hint_rect.top = text_coord2
                                hint_rect.x = 260
                                hint_rect.y += 30
                                text_coord2 += hint_rect.height * 1.2
                                screen.blit(string_rendered, hint_rect)
                        else:
                            show_hint = False
                            screen.blit(fon, (240, 300), pygame.Rect(240, 300, 550, 150))
            elif event.type == pygame.QUIT:
                terminate()
            manager.process_events(event)
            manager.update(time_delta)
            manager.draw_ui(screen)
            pygame.display.flip()
            clock.tick(50)


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10,
                                              text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOWS_SIZE)
    background_image = pygame.image.load("data/background.jpg").convert()
    background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background_surface.blit(background_image, (0, 0))
    pygame.display.set_caption('start')

    manager = pygame_gui.UIManager(WINDOWS_SIZE)
    maze = maze_generator.generate_maze(25, 25)
    maze_generator.save_maze(maze, 'maps/map.txt')

    labyrinth = Labyrinth("map.txt", [0, 2, 4], 4, 2)
    random_coordinates = get_random_free_coordinate(labyrinth.is_free)
    hero = Hero(random_coordinates[0])
    enemy = Enemy(random_coordinates[1])
    coins_positions = labyrinth.generate_coins(10)  # генерируем позиции для 10 морковок
    coins = [Coin(pos) for pos in coins_positions]

    game = Game(labyrinth, hero, enemy, coins)
    ui = UI(game)
    pygame.mixer.music.load('data/music.mp3')
    pygame.mixer_music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    start_screen(screen, ui, manager, game)

    ui.menu(manager)
    running = True
    game_over = False
    game_over_sound_played = False
    win_sound_played = False
    short_sound_allowed = True

    while running:
        game.labyrinth.update_from_file("maps/map.txt")
        if game.level_coins % 5 == 0 and game.level_coins != 0:
            if game.levels == 1:
                update_wall_to_win("maps/map.txt")
            else:
                update_wall_to_exit("maps/map.txt")

        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if game_over is False:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == ui.k_pause:
                            game.switch_pause()
                        elif event.ui_element == ui.k_save:
                            ui.save_game()

                        elif event.ui_element == ui.k_load:
                            ui.load_game()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == ui.k_restart:
                        game_over_sound_played = False
                        win_sound_played = False
                        pygame.mixer.music.play(-1)
                        manager = pygame_gui.UIManager(WINDOWS_SIZE)
                        maze = maze_generator.generate_maze(25, 25)
                        maze_generator.save_maze(maze, 'maps/map.txt')
                        labyrinth = Labyrinth("map.txt", [0, 2, 4], 4, 2)

                        de = enemy.get_delay()
                        random_coordinates = get_random_free_coordinate(labyrinth.is_free)
                        hero = Hero(random_coordinates[0])
                        enemy = Enemy(random_coordinates[1])

                        enemy.set_delay(de)
                        coins_positions = labyrinth.generate_coins(10)  # генерируем позиции для 10 морковок
                        coins = [Coin(pos) for pos in coins_positions]
                        so = game.get_short_sound_allowed()
                        game = Game(labyrinth, hero, enemy, coins)
                        game.set_short_sound_allowed(so)
                        ui = UI(game)
                        ui.menu(manager)
                        running = True
                        game_over = False
                    elif event.ui_element == ui.k_diff:
                        game_over_sound_played = False
                        win_sound_played = False
                        pygame.mixer.music.play(-1)
                        manager = pygame_gui.UIManager(WINDOWS_SIZE)

                        maze = maze_generator.generate_maze(25, 25)
                        maze_generator.save_maze(maze, 'maps/map.txt')
                        labyrinth = Labyrinth("map.txt", [0, 2, 4], 4, 2)
                        random_coordinates = get_random_free_coordinate(labyrinth.is_free)
                        hero = Hero(random_coordinates[0])
                        enemy = Enemy(random_coordinates[1])
                        coins_positions = labyrinth.generate_coins(10)  # генерируем позиции для 10 морковок
                        coins = [Coin(pos) for pos in coins_positions]
                        so = game.get_short_sound_allowed()
                        game = Game(labyrinth, hero, enemy, coins)
                        game.set_short_sound_allowed(so)
                        ui = UI(game)
                        start_screen(screen, ui, manager, game)
                        ui.menu(manager)
                        running = True
                        game_over = False
                    elif event.ui_element == ui.k_music:
                        if pygame.mixer.music.get_volume() == 0.296875:
                            pygame.mixer.music.set_volume(0)
                        else:
                            pygame.mixer.music.play(-1)
                            pygame.mixer.music.set_volume(0.3)
                    elif event.ui_element == ui.k_sound:
                        if short_sound_allowed is True:
                            short_sound_allowed = False
                            game.short_sound_allowed = False
                        else:
                            short_sound_allowed = True
                            game.short_sound_allowed = True

            if event.type == ENEMY_EVENT_TYPE and not game_over:
                game.move_enemy()
            manager.process_events(event)
        manager.update(time_delta)
        if not game_over and not game.is_paused:
            game.update_hero()
        screen.fill((123, 123, 123))
        game.render(screen)
        if game.check_win():
            if win_sound_played is False and short_sound_allowed is True:
                pygame.mixer.music.stop()
                sound2 = pygame.mixer.Sound("data/win.mp3")
                sound2.set_volume(10)
                sound2.play()
                win_sound_played = True
            game_over = True
            show_message(screen, "ПОБЕДА!")
        if game.check_level():
            manager = pygame_gui.UIManager(WINDOWS_SIZE)
            maze = maze_generator.generate_maze(25, 25)
            maze_generator.save_maze(maze, 'maps/map.txt')
            labyrinth = Labyrinth("map.txt", [0, 2, 4], 4, 2)
            de = enemy.get_delay()
            random_coordinates = get_random_free_coordinate(labyrinth.is_free)
            hero = Hero(random_coordinates[0])
            enemy = Enemy(random_coordinates[1])
            enemy.set_delay(de)
            coins_positions = labyrinth.generate_coins(10)  # генерируем позиции для 10 морковок
            coins = [Coin(pos) for pos in coins_positions]
            so = game.get_short_sound_allowed()
            gcoins = game.get_collected_coins()
            levels = game.get_levels() - 1
            game = Game(labyrinth, hero, enemy, coins)
            game.set_collected_coins(gcoins)
            game.set_levels(levels)
            game.set_short_sound_allowed(so)
            ui = UI(game)
            ui.menu(manager)
            running = True
            game_over = False
        if game.check_lose():
            if game_over_sound_played is False and short_sound_allowed is True:
                pygame.mixer.music.stop()
                sound2 = pygame.mixer.Sound("data/defeat.mp3")
                sound2.set_volume(10)
                sound2.play()
                game_over_sound_played = True
            game_over = True
            show_message(screen, "Упс...")

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
