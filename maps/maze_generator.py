import random

def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]

    # Рекурсивная функция для создания лабиринта
    def create_path(x, y):
        maze[y][x] = 0

        # Список направлений
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                create_path(nx, ny)

    # Создание лабиринта из (1, 1)
    create_path(1, 1)

    # Добавление входа
    maze[1][0] = 0  # Вход

    # Добавление рамки
    for y in range(height):
        maze[y][0] = 1
        maze[y][width - 1] = 1
    for x in range(width):
        maze[0][x] = 1
        maze[height - 1][x] = 1

    # Добавление прохода к выходу на рамке
    exit_side = random.randint(0, 3)  # Сторона, на которой будет выход (0 - верх, 1 - право, 2 - низ, 3 - лево)
    if exit_side == 0:  # верх
        exit_x = random.randint(1, width - 2)
        maze[0][exit_x] = 2  # Выход
        maze[1][exit_x] = 0  # Проход к выходу
    elif exit_side == 1:  # право
        exit_y = random.randint(1, height - 2)
        maze[exit_y][width - 1] = 2  # Выход
        maze[exit_y][width - 2] = 0  # Проход к выходу
    elif exit_side == 2:  # низ
        exit_x = random.randint(1, width - 2)
        maze[height - 1][exit_x] = 2  # Выход
        maze[height - 2][exit_x] = 0  # Проход к выходу
    else:  # лево
        exit_y = random.randint(1, height - 2)
        maze[exit_y][0] = 2  # Выход
        maze[exit_y][1] = 0  # Проход к выходу

    # Добавление дополнительных проходов
    for _ in range(width * height // 6):  # Примерно 1/8 от общего количества клеток
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if maze[y][x] == 1:
            maze[y][x] = 0

    return maze

def save_maze(maze, filename):
    with open(filename, 'w') as f:
        for row in maze:
            line = ' '.join(map(str, row))
            f.write(line + '\n')

def print_maze(maze):
    for row in maze:
        print(' '.join(map(str, row)))
