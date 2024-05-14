import random as rnd


# ============================================
def print_error(str_: str) -> None:
    print("Ошибка:", str_)
    print()


def say_as_comp(str_):
    print(f">> {str_}")


# ============================================
class Point:
    def __init__(self, x, y) -> None:
        self.__x = x
        self.__y = y

    def __str__(self) -> str:
        return f"[x = {self.__x}, y = {self.__y}]"

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

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
# класс внутриигрового сообщения
class GameEvent:
    Event_Shot = 1              # событие выстрела одного из игроков
    Event_Win = 2               # событие выигрыша одного из игроков
    Event_Computer_Move = 3     # событие, предваряэщее ход компьютерного игрока
    Event_Quit = 99             # Выход

    def __init__(self, event_type: int, player=None, event_data=None) -> None:
        self.__type = event_type
        self.__player = player
        self.__data = event_data

    @property
    def type(self):
        return self.__type

    @property
    def player(self):
        return self.__player

    @property
    def data(self):
        return self.__data


# ---------------------------------
# класс корабля
class Ship:
    State = {
        'killed': 0,
        'injured': 1,
        'missed': 2,
        'alive': 9
    }

    def __init__(self, body_coordinates: list[Point]) -> None:
        self.__body = set()
        self.__hits = set()
        if Ship.may_exist(body_coordinates):
            for p in body_coordinates:
                self.__body.add(p)
                self.__hits.add(p)
            self.__state = Ship.State['alive']
            self.__size = len(self.__body)
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

    def hit(self, shot: Point) -> bool:
        for p in self.body:
            if p == shot:
                return True
        return False

    # ToDo: обработка ошибки при попытки извлечь из списка точку, которой там нет
    def reduce(self, point: Point) -> None:
        self.__hits.remove(point)
        if len(self.__hits):
            self.__state = Ship.State['injured']
        else:
            self.__state = Ship.State['killed']

    def __str__(self) -> str:
        ret = f"Корабль длиной {self.__size}: "
        for p in self.body:
            ret = ret + str(p)
        return ret

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.body == other.body

    def __hash__(self):
        return hash(tuple(self.body))

    @property
    def body(self) -> set[Point]:
        return self.__body

    @property
    def size(self) -> int:
        return self.__size

    @property
    def state(self) -> int:
        return self.__state

    @property
    def nearby(self) -> set[Point]:
        neighbors = set()
        for p in self.body:
            neighbors.add(Point(p.x + 1, p.y))
            neighbors.add(Point(p.x - 1, p.y))
            neighbors.add(Point(p.x, p.y - 1))
            neighbors.add(Point(p.x, p.y + 1))
            # neighbors.add(Point(p.x + 1, p.y + 1))
            # neighbors.add(Point(p.x + 1, p.y - 1))
            # neighbors.add(Point(p.x - 1, p.y + 1))
            # neighbors.add(Point(p.x - 1, p.y - 1))
        for p in self.body:
            neighbors.discard(p)
        return neighbors


# ---------------------------------
# класс игрового поля
class SeaBattleGameBoard:
    Fog_Of_War = 0
    Sea_Spot = 1
    Ship_Body = 2
    Miss_Shot = 3
    Hit_Shot = 4
    Ship_Neighbor = 5

    def __init__(self, size: int, ships: list[Ship]) -> None:
        self.__board_size = size
        self.__board = [[SeaBattleGameBoard.Sea_Spot for x in range(self.__board_size)] for y in range(self.__board_size)]
        self.__enemy_shots = [[SeaBattleGameBoard.Fog_Of_War for x in range(self.__board_size)]
                              for y in range(self.__board_size)]
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

    @property
    def board(self):
        return self.__board

    @property
    def size(self) -> int:
        return self.__board_size

    @property
    def enemy_shots(self):
        return self.__enemy_shots

    def incoming_shot(self, shot: Point) -> bool:
        if self.__enemy_shots[shot.x - 1][shot.y - 1] not in [SeaBattleGameBoard.Fog_Of_War, SeaBattleGameBoard.Ship_Neighbor]:
            raise ValueError
        for ship in self.__ships:
            if ship.hit(shot):
                ship.reduce(shot)
                if ship.state == Ship.State['injured']:
                    say_as_comp("Ранил")
                    self.__enemy_shots[shot.x - 1][shot.y - 1] = SeaBattleGameBoard.Hit_Shot
                    return True
                elif ship.state == Ship.State['killed']:
                    say_as_comp("Убил!")
                    self.__enemy_shots[shot.x - 1][shot.y - 1] = SeaBattleGameBoard.Hit_Shot
                    self.__alive_ships_count -= 1
                    for p in ship.nearby:
                        try:
                            if self.__enemy_shots[p.x - 1][p.y - 1] == SeaBattleGameBoard.Fog_Of_War:
                                self.__enemy_shots[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Neighbor
                        except IndexError:
                            continue
                    return True
        else:
            say_as_comp("Мимо ))")
            self.__enemy_shots[shot.x - 1][shot.y - 1] = SeaBattleGameBoard.Miss_Shot
            return False


# Класс Player, предназначенный для переопределения
class Player:
    def __init__(self, name):
        self.__name = name
        self.__board = None
        self.__enemy = None
        self.__last_shot_success = True

    def init_ships(self) -> list[Ship]:
        ships = []
        return ships

    def get_move(self) -> GameEvent:
        pass

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def board(self) -> SeaBattleGameBoard:
        return self.__board

    @board.setter
    def board(self, board) -> None:
        self.__board = board

    @property
    def enemy(self):
        return self.__enemy

    @enemy.setter
    def enemy(self, enemy_player) -> None:
        self.__enemy = enemy_player

    @property
    def last_shot_success(self) -> bool:
        return self.__last_shot_success

    @last_shot_success.setter
    def last_shot_success(self, status: bool) -> None:
        self.__last_shot_success = status


class HumanPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    # Подготовка кораблей в интерактивном режиме
    def init_ships(self) -> list[Ship]:
        ships = [
            Ship([Point(5, 2), Point(5, 3), Point(5, 4)]),
            Ship([Point(1, 1), Point(1, 2)]),
            Ship([Point(2, 4), Point(3, 4)]),
            Ship([Point(1, 6)]),
            Ship([Point(5, 6)]),
            Ship([Point(3, 6)]),
            Ship([Point(3, 2)])
        ]
        return ships

    # Получаем от пользователя его ход с обработкой различных исключений
    def get_move(self) -> GameEvent:
        while True:
            try:
                str_ = input("Введите координаты, разделенные пробелом (X Y), "
                             "куда вы хотите выстрелить (q для выхода): ")
            except KeyboardInterrupt:
                return GameEvent(GameEvent.Event_Quit)

            if not str_:
                print("Не надо бояться - стреляете!")
                continue

            if str_[0] == 'q':
                return GameEvent(GameEvent.Event_Quit)

            try:
                x, y = map(int, str_.split())
            except ValueError:
                print_error(f"Непохоже, что вы указали верные координаты: '{str_}'")
                print("Попробуйте еще раз")
                continue

            if x not in range(1, self.board.size + 1) or y not in range(1, self.board.size + 1):
                print_error(f"Вы стреляете в пустоту! Координаты ({x}, {y}) находятся за пределами "
                            f"игрового поля {self.board.size}x{self.board.size}")
                print("Попробуйте еще раз")
                continue
            else:
                return GameEvent(GameEvent.Event_Shot, self, Point(x, y))


# класс компьютерного игрока
class ComputerPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.__possible_moves = []

    # Автоматическая генерация кораблей случайным образом
    def init_ships_old(self) -> list[Ship]:
        ships = [
            Ship([Point(1, 1), Point(2, 1), Point(3, 1)]),
            Ship([Point(4, 2), Point(5, 2)]),
            Ship([Point(5, 4), Point(5, 5)]),
            Ship([Point(1, 4)]),
            Ship([Point(3, 4)]),
            Ship([Point(1, 6)]),
            Ship([Point(3, 6)])
        ]
        return ships

    def tmp_draw(self, board_size, board) -> None:
        # Вывод заголовка с номерами столбцов
            print()
            row = ' '
            for x in range(board_size):
                row = row + ' ' + str(x + 1)
            print("{:<15}".format(row))

            # Построчный вывод на консоль полей с номерами строк (координата y) в начале каждой строки
            for y in range(board_size):
                row = str(y + 1)
                for x in range(board_size):
                    row = row + ' ' + str(board[x][y])
                print("{:<15}".format(row))

    def init_ships(self) -> list[Ship]:
        board_size = 6      # пока непонятно, откуда это здесь возмется
        tmp_board = [[SeaBattleGameBoard.Fog_Of_War for x in range(board_size)] for y in range(board_size)]
        ships = []
        ships_quantity = {
            3: 1,
            2: 2,
            1: 4
        }

        for ship_size in ships_quantity.keys():
            print(f"Генерим {ships_quantity[ship_size]} кораблей длиной {ship_size}:")
            possible_ships = set()
            for y in range(1, board_size + 1):
                for x in range(1, board_size + 2 - ship_size):
                    p = []
                    for z in range(ship_size):
                        p.append(Point(x + z, y))
                    ship = Ship(p)
                    possible_ships.add(ship)
                    # print(f"{ship}")
            # print("=========")
            for x in range(1, board_size + 1):
                for y in range(1, board_size +2 - ship_size):
                    p = []
                    for z in range(ship_size):
                        p.append(Point(x, y + z))
                    ship = Ship(p)
                    possible_ships.add(ship)
                    # print(f"{ship}")
            list_of_candidates = list(possible_ships)

            for _ in range(ships_quantity[ship_size]):
                ship_found = False
                while not ship_found:
                    try:
                        num = rnd.randint(0, len(list_of_candidates) - 1)
                        ship = list_of_candidates[num]
                        for p in ship.body:
                            if tmp_board[p.x - 1][p.y - 1] != SeaBattleGameBoard.Fog_Of_War:
                                # корабль пытается встать на занятые клетки
                                break
                        else:
                            # корабль подходит
                            print(f">> Выбираем {num} из {len(list_of_candidates)}: {ship}")
                            ships.append(ship)
                            for p in ship.body:
                                tmp_board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Body
                            for p in ship.nearby:
                                if p.x in range(1, board_size + 1) and p.y in range(1, board_size + 1):
                                    tmp_board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Sea_Spot
                            ship_found = True
                    except IndexError as e:
                        continue
                    #self.tmp_draw(board_size, tmp_board)

        return ships

    def generate_moves(self) -> None:
        for y in rnd.sample(range(self.board.size), self.board.size):
            for x in rnd.sample(range(self.board.size), self.board.size):
                self.__possible_moves.append(Point(x + 1, y + 1))

    def get_move(self) -> GameEvent:
        i = rnd.randint(0, len(self.__possible_moves) - 1)
        comp_shot = self.__possible_moves[i]
        self.__possible_moves.pop(i)
        print(f"{self.name} стреляет {comp_shot}")
        return GameEvent(GameEvent.Event_Shot, self, comp_shot)

    @property
    def board(self) -> SeaBattleGameBoard:
        return self.__board

    @board.setter
    def board(self, board) -> None:
        self.__board = board
        self.generate_moves()

# ---------------------------------
# класс логики игры "Морской бой"
class SeaBattleGameLogic:
    def __init__(self, size: int, player1: Player, player2: Player) -> None:
        self.__board_size = size
        self.__player1 = player1
        self.__player2 = player2
        self.__player1.enemy = player2
        self.__player2.enemy = player1
        self.__player1.board = SeaBattleGameBoard(size, self.__player1.init_ships())
        self.__player2.board = SeaBattleGameBoard(size, self.__player2.init_ships())

    @property
    def player1(self):
        return self.__player1

    @property
    def player2(self):
        return self.__player2

    def process_event(self, event: GameEvent):
        try:
            if event.type == GameEvent.Event_Shot:
                if event.player.enemy.board.incoming_shot(event.data):
                    event.player.last_shot_success = True
                else:
                    event.player.last_shot_success = False
                    event.player.enemy.last_shot_success = True
        except ValueError:
            print_error("Вы сюда уже стреляли!")

    @property
    def is_player1_win(self) -> bool:
        return not self.__player2.board.alive_ships_count

    @property
    def is_player2_win(self) -> bool:
        return not self.__player1.board.alive_ships_count


if __name__ == "__main__":

    board_size = 6
    user = ComputerPlayer('Компутер')
    user.board = SeaBattleGameBoard(board_size, user.init_ships())
    print(user.name)
    print(user.board)

    # logic = SeaBattleGameLogic(board_size)
    # logic.user_board._draw()
    # print(f"На поле {logic.user_board.alive_ships_count} живых кораблей")

    # ship_1 = Ship([Point(5, 2), Point(5, 3), Point(5, 4)])
    # ship_2 = Ship([Point(1, 1), Point(1, 2)])
    # ship_3 = Ship([Point(2, 4), Point(3, 4)])
    # ship_4 = Ship([Point(1, 6)])
    # ship_5 = Ship([Point(5, 6)])
    # ship_6 = Ship([Point(3, 6)])
    # ship_7 = Ship([Point(3, 2)])

    # my_ships = [ship_1, ship_2, ship_3, ship_4, ship_5, ship_6, ship_7]
#     board_size = 6
#     my_board = SeaBattleGameBoard(board_size, my_ships)
#     print(f"На поле {my_board.alive_ships_count} живых кораблей")
#
#     my_board._draw()
#     # print(my_board)

