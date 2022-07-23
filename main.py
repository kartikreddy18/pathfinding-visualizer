
from operator import ne
from queue import PriorityQueue
from matplotlib.pyplot import close
import pygame


width = 700
screen = pygame.display.set_mode((width, width), pygame.NOFRAME)
clock = pygame.time.Clock()
fps = 30

black = '#000000'
white = '#f1f1f1'  # default
green = '#90C8AC'  # open
red = '#D61C4E'  # closed
orange = '#FEB139'  # start
purple = '#937DC2'  # path
navy = '#293462'  # barrier
teal = '#18978F'  # end


class Spot:
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col
        self.color = white
        self.x = row * width
        self.y = col * width
        self.neighbor: list[Spot] = []
        self.total_rows = total_rows
        self.width = width

    def is_open(self) -> bool:
        return self.color == green

    def is_closed(self) -> bool:
        return self.color == red

    def is_barrier(self) -> bool:
        return self.color == navy

    def is_start(self) -> bool:
        return self.color == orange

    def is_end(self) -> bool:
        return self.color == teal

    def make_open(self) -> None:
        self.color = green

    def make_closed(self) -> None:
        self.color = red

    def make_start(self) -> None:
        self.color = orange

    def make_end(self) -> None:
        self.color = teal

    def make_path(self) -> None:
        self.color = purple

    def make_barrier(self) -> None:
        self.color = navy

    def reset(self) -> None:
        self.color = white

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width, self.width))

    def get_pos(self) -> tuple[int, int]:
        return self.x, self.y

    def update_neighbor(self, grid: list[list]) -> None:
        self.neighbor = []
        if self.row > 0 and not (grid[self.row - 1][self.col]).is_barrier():  # UP
            self.neighbor.append(grid[self.row - 1][self.col])
        # DOWN
        if self.row < self.total_rows - 1 and not (grid[self.row + 1][self.col]).is_barrier():
            self.neighbor.append(grid[self.row + 1][self.col])
        if self.col > 0 and not (grid[self.row][self.col - 1]).is_barrier():  # LEFT
            self.neighbor.append(grid[self.row][self.col - 1])
        # RIGHT
        if self.col < self.total_rows - 1 and not (grid[self.row][self.col + 1]).is_barrier():
            self.neighbor.append(grid[self.row][self.col + 1])


def h(p1: tuple[int, int], p2: tuple[int, int]) -> int:
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def make_grid(rows: int, width: int) -> list[list]:
    gap = width // rows
    return [[Spot(row, col, gap, rows) for col in range(rows)] for row in range(rows)]


def draw_grid(rows: int, width: int, screen: pygame.Surface) -> None:
    gap = width // rows
    for row in range(rows):
        pygame.draw.aaline(screen, black, (row * gap, 0), (row * gap, width))
        pygame.draw.aaline(screen, black, (0, row * gap), (width, row * gap))


def draw(screen: pygame.Surface, grid: list[list], rows: int) -> None:
    screen.fill(black)
    clock.tick(fps)
    for row in grid:
        for spot in row:
            spot.draw(screen)
    draw_grid(rows, width, screen)
    pygame.display.update()


def get_clicked_pos(pos: tuple[int, int], rows: int, width: int) -> tuple[int, int]:
    gap = width // rows
    x, y = pos
    row = x // gap
    col = y // gap
    return row, col


def reconstruct_path(draw, came_from: dict[Spot], current: Spot):
    while current in came_from:
        current = came_from[current]
        current.make_path()
    draw()


def a_star_algorithm(draw, grid: list[list], start: Spot, end: Spot) -> bool:
    count = 0
    open_set: PriorityQueue[tuple[int, int, Spot]] = PriorityQueue()
    came_from = {}
    open_set.put((0, count, start))
    closed_set = {start}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float('inf') for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)

        current = open_set.get()[2]
        closed_set.remove(current)

        if current == end:
            reconstruct_path(draw, came_from, end)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbor:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())

                if neighbor not in closed_set:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    closed_set.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()

    return False


def dj(draw, grid: list[list[Spot]], start: Spot, end: Spot) -> bool:
    count = 0
    open_set: PriorityQueue[tuple[float, int, Spot]] = PriorityQueue()
    closed_set = {start}
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    open_set.put((g_score[start], count, start))
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)

        current = open_set.get()[2]
        closed_set.remove(current)

        if current == end:
            reconstruct_path(draw, came_from, end)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbor:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                g_score[neighbor] = temp_g_score
                came_from[neighbor] = current

                if neighbor not in closed_set:
                    count += 1
                    open_set.put((g_score[neighbor], count, neighbor))
                    closed_set.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False


def gbfs(draw, grid: list[list[Spot]], start: Spot, end: Spot) -> bool:
    count = 0
    open_set: PriorityQueue[tuple[float, int, Spot]] = PriorityQueue()
    closed_set = {start}
    came_from = {}
    h_score = {spot: float("inf") for row in grid for spot in row}
    h_score[start] = h(start.get_pos(), end.get_pos())
    open_set.put((h_score[start], count, start))
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)

        current = open_set.get()[2]
        closed_set.remove(current)

        if current == end:
            reconstruct_path(draw, came_from, end)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbor:
            temp_h_score = h(neighbor.get_pos(), end.get_pos())
            if temp_h_score < h_score[neighbor]:
                came_from[neighbor] = current
                h_score[neighbor] = temp_h_score
                if neighbor not in closed_set:
                    count += 1
                    open_set.put((h_score[neighbor], count, neighbor))
                    closed_set.add(neighbor)
                    neighbor.make_open()

        draw()
        if current != start:
            current.make_closed()
    return False


def main(screen: pygame.Surface, width: int) -> None:
    run = True
    start = False
    end = False
    rows = 50
    grid = make_grid(rows, width)
    algorithm = 0

    while run:
        draw(screen, grid, rows)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                if event.key == pygame.K_t:
                    algorithm += 1
                    algorithm %= 3

                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbor(grid)
                    if algorithm == 0:
                        print("A* algorithm")
                        a_star_algorithm(lambda: draw(
                            screen, grid, rows), grid, start, end)
                    elif algorithm == 1:
                        print("Dijkstra's algorithm")
                        dj(lambda: draw(screen, grid, rows), grid, start, end)
                    else:
                        print("Greedy Best First Search Algorithm")
                        gbfs(lambda: draw(screen, grid, rows), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot: Spot = grid[row][col]

                if spot != end and not start:
                    start = spot
                    start.make_start()
                elif spot != start and not end:
                    end = spot
                    end.make_end()
                elif spot != start and spot != end and start and end:
                    spot.make_barrier()

            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot: Spot = grid[row][col]
                if spot.is_start():
                    start = None
                elif spot.is_end():
                    end = None
                spot.reset()

    pygame.quit()
    exit(0)


if __name__ == '__main__':
    main(screen, width)
