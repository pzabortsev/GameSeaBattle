
# ============================================
def print_error(str_: str) -> None:
    print("Ошибка:", str_)


# ============================================
class Point:
    def __init__(self, x, y) -> None:
        self.__x = x
        self.__y = y

    def __str__(self) -> str:
        return f"[x = {self.__x}, y = {self.__y}]"

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @x.setter
    def x(self, x: int) -> None:
        self.__x = x

    @y.setter
    def y(self, y: int) -> None:
        self.__y = y


# ---------------------------------
# класс корабля
class Ship:
    def __init__(self, body_coordinates: list[Point]) -> None:
        self.__body = []
        self.__size = 0
        if Ship.may_exist(body_coordinates):
            for p in body_coordinates:
                self.__body.append(p)
                self.__size += 1
        else:
            print_error("Корабль не может быть такой конфигурации")

    # Проверяет, можно ли из полученных координат составить корабль
    # ToDo: нужно еще проверить, что в корабле нет разрывов
    @staticmethod
    def may_exist(points: list[Point]) -> bool:
        num_of_points = len(points)

        if num_of_points == 1:
            return True

        _xx = _yy = 0
        for p in points:
            _xx = _xx + p.x
            _yy = _yy + p.y

        _vertical = _xx / num_of_points == points[0].x
        _horizontal = _yy / num_of_points == points[0].y
        if (_vertical and not _horizontal) or (_horizontal and not _vertical):
            return True
        else:
            return False

    def __str__(self) -> str:
        ret = f"Корабль длиной {self.__size}: "
        for p in self.__body:
            ret = ret + str(p)
        return ret

    @property
    def body(self) -> list[Point]:
        return self.__body

    @property
    def size(self) -> int:
        return self.__size


# ---------------------------------
# класс игрового поля
class SeaBattleGameBoard:
    Ship_Body = 1
    Sea_Spot = 0
    Fog_Of_War = -1

    def __init__(self, size: int, ships: list[Ship]) -> None:
        self.__board_size = size
        self.__board = [[SeaBattleGameBoard.Sea_Spot for x in range(self.__board_size)] for y in range(self.__board_size)]
        self.__enemy_shoots = [[SeaBattleGameBoard.Fog_Of_War for x in range(self.__board_size)] for y in range(self.__board_size)]
        self.__ships = []
        self.__alive_ships_count = 0
        for ship in ships:
            self.add_ship(ship)

    # Добавляет корабль на поле
    # Перед добавлением корабля делает следующие проверки:
    #   - длина корабля должна быть 1, 2 или 3
    #   - корабль должен располагаться внутри поля
    #   - ToDo: расстояние от имеющихся кораблей должно составлять минимум одну клетку
    def add_ship(self, ship: Ship) -> bool:
        ret = True
        if ship.size not in [1, 2, 3]:
            print_error(f"Разрешены корабли длиной 1, 2 или 3 ({ship.size = })")
            return False

        for p in ship.body:
            if p.x not in range(1, self.__board_size + 1) or p.y not in range(1, self.__board_size + 1):
                print_error(f"Координаты корабля {ship} находятся за пределами игрового поля")
                return False

        for p in ship.body:
            self.__board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Body
        self.__ships.append(ship)
        self.__alive_ships_count += 1

        return True

    def __str__(self) -> str:
        ret = f"Игровое поле размером {self.__board_size}x{self.__board_size}:\n"
        for ship in self.__ships:
            ret = ret + str(ship) + '\n'
        return ret

    @property
    def alive_ships_count(self):
        return self.__alive_ships_count

    def _draw(self):
        # Вывод заголовка с номерами столбцов
        print()
        row = ' '
        for x in range(self.__board_size):
            row = row + ' ' + str(x + 1)

        row = row + '     ' + row
        print(row)

        # Построчный вывод на консоль поля с номером строки в начале каждой строки
        # Первым выводится поле ????
        for y in range(self.__board_size):
            row = str(y + 1)
            for x in range(self.__board_size):
                row = row + ' ' + str(self.__enemy_shoots[x][y])
            row = row + '     ' + str(y + 1)
            for x in range(self.__board_size):
                row = row + ' ' + str(self.__board[x][y])
            print(row)


# ---------------------------------
# класс внутриигрового сообщения
class GameEvent:
    Event_None = 0          # пустое событие
    Event_Tick = 1          # событие таймера
    Event_Hit = 2           # событие "выстрела" по цели
    Event_Quit = 99         # Выход

    def __init__(self, event_type, event_data) -> None:
        self.__type = event_type
        self.__data = event_data

    @property
    def type(self):
        return self.__type

    @property
    def data(self):
        return self.__data


# ---------------------------------
# класс логики игры "Морской бой"
class SeaBattleGameLogic:
    def __init__(self, size: int) -> None:
        self.__board_size = size
        self.__user_board = SeaBattleGameBoard()
        self.__comp_board = SeaBattleGameBoard()

    def get_user_board(self):
        return self.__user_board

    def process_event(self, event):
        pass

    def hit(self, point):
        pass


if __name__ == "__main__":
    ship_1 = Ship([Point(5, 2), Point(5, 3), Point(5, 4)])
    ship_2 = Ship([Point(1, 1), Point(1, 2)])
    ship_3 = Ship([Point(2, 4), Point(3, 4)])
    ship_4 = Ship([Point(1, 6)])
    ship_5 = Ship([Point(5, 6)])
    ship_6 = Ship([Point(3, 6)])
    ship_7 = Ship([Point(3, 2)])

    my_ships = [ship_1, ship_2, ship_3, ship_4, ship_5, ship_6, ship_7]
    board_size = 6
    my_board = SeaBattleGameBoard(board_size, my_ships)
    print(f"На поле {my_board.alive_ships_count} живых кораблей")

    my_board._draw()
    # print(my_board)

