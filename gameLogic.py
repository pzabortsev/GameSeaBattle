import random as rnd


# ============================================
def print_error(str_: str) -> None:
    print("Ошибка:", str_)
    print()


# ToDo: подумать, как реализовать эту функцию в GUI. И ту, что выше
def say_as_comp(str_):
    print(f">> {str_}")


# ============================================
class Point:
    def __init__(self, x, y) -> None:
        self.__x = x
        self.__y = y

    def __str__(self) -> str:
        return f"[x = {self.x}, y = {self.y}]"

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

    def in_board(self, board) -> bool:
        return self.x in range(1, board.size + 1) and self.y in range(1, board.size + 1)


# ---------------------------------
# класс внутриигрового сообщения
class GameEvent:
    Event_Shot = 1              # событие выстрела одного из игроков
    Event_Win = 2               # событие выигрыша одного из игроков
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
    State_Killed = 0
    State_Injured = 1
    State_Alive = 9

    def __init__(self, body: list[Point]) -> None:
        self.__body = set()
        self.__hits = set()
        if Ship.may_exist(body):
            for p in body:
                self.__body.add(p)
                self.__hits.add(p)
            self.__state = Ship.State_Alive
            self.__size = len(self.__body)
        else:
            print_error("Корабль не может быть такой конфигурации")
            raise ValueError

    # Проверяет, можно ли из полученных координат построить корабль:
    # - все точки должны лежать на одной прямой
    # - в корабле не должно быть разрывов
    @staticmethod
    def may_exist(points: list[Point]) -> bool:
        num_of_points = len(points)

        if num_of_points == 1:
            return True

        _xx = _yy = 0
        _min_x = _max_x = points[0].x
        _min_y = _max_y = points[0].y
        for p in points:
            _min_x = p.x if p.x < _min_x else _min_x
            _min_y = p.y if p.y < _min_y else _min_y
            _max_x = p.x if p.x > _max_x else _max_x
            _max_y = p.y if p.y > _max_y else _max_y
            _xx = _xx + p.x
            _yy = _yy + p.y

        _vertical = (_xx / num_of_points == _min_x) and (_max_y - _min_y == num_of_points - 1)
        _horizontal = (_yy / num_of_points == _min_y) and (_max_x - _min_x == num_of_points - 1)

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
            self.__state = Ship.State_Injured
        else:
            self.__state = Ship.State_Killed

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
            neighbors.discard(p)
        return neighbors


# ---------------------------------
# класс игрового поля
class SeaBattleGameBoard:
    Fog_Of_War = 0
    Sea_Spot = 1
    Ship_Body = 2
    Ship_Neighbor = 3
    Miss_Shot = 4
    Hit_Shot = 5

    def __init__(self, size: int, ships: list[Ship]) -> None:
        self.__board_size = size
        self.__board = [[SeaBattleGameBoard.Sea_Spot for _ in range(self.__board_size)] for _ in range(self.__board_size)]
        self.__enemy_shots = [[SeaBattleGameBoard.Fog_Of_War for _ in range(self.__board_size)]
                              for _ in range(self.__board_size)]
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
        if ship.size not in [1, 2, 3]:
            print_error(f"Разрешены корабли длиной 1, 2 или 3 ({ship.size = })")
            return False

        for p in ship.body:
            if not p.in_board(self):
                print_error(f"Координаты корабля {ship} находятся за пределами игрового поля")
                return False

        for p in ship.body:
            self.__board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Body
        self.__ships.append(ship)
        self.__alive_ships_count += 1

        return True

    def __str__(self) -> str:
        ret = f"Игровое поле размером {self.size}x{self.size}:\n"
        for ship in self.__ships:
            ret = ret + str(ship) + '\n'
        return ret

    @property
    def size(self) -> int:
        return self.__board_size

    @property
    def alive_ships_count(self) -> int:
        return self.__alive_ships_count

    @property
    def board(self) -> list[list[int]]:
        return self.__board

    @property
    def enemy_shots(self) -> list[list[int]]:
        return self.__enemy_shots

    # Обрабатывает выстрел нашего противника:
    # - выбрасывает исключение, если выстрел попал в ту же воронку
    # - если выстрел попал в один из наших кораблей, то меняет статус корабля (Ранен/Убит)
    # - возвращает признак, успешный или неуспешный был выстрел
    def incoming_shot(self, shot: Point) -> bool:
        if (self.enemy_shots[shot.x - 1][shot.y - 1] not in
                [SeaBattleGameBoard.Fog_Of_War, SeaBattleGameBoard.Ship_Neighbor]):
            raise ValueError
        ret = None
        for ship in self.__ships:
            if ship.hit(shot):
                self.enemy_shots[shot.x - 1][shot.y - 1] = SeaBattleGameBoard.Hit_Shot
                ship.reduce(shot)
                if ship.state == Ship.State_Injured:
                    say_as_comp("Ранил")
                elif ship.state == Ship.State_Killed:
                    say_as_comp("Убил!")
                    self.__alive_ships_count -= 1
                    for p in ship.nearby:
                        if p.in_board(self):
                            if self.enemy_shots[p.x - 1][p.y - 1] == SeaBattleGameBoard.Fog_Of_War:
                                self.enemy_shots[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Neighbor
                ret = True
                break
        else:
            say_as_comp("Мимо ))")
            self.enemy_shots[shot.x - 1][shot.y - 1] = SeaBattleGameBoard.Miss_Shot
            ret = False

        return ret


# Класс Player, предназначенный для переопределения
class Player:
    def __init__(self, name):
        self.__name = name
        self.__board = None
        self.__enemy = None
        self.__last_shot_success = True

    def init_ships(self, board_size: int, ships_quantity: dict) -> list[Ship]:
        ships = []
        return ships

    def get_move(self) -> GameEvent:
        pass

    def congrats(self) -> str:
        return ''

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

    @property
    def is_winner(self) -> bool:
        return not self.enemy.board.alive_ships_count


class HumanPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    # Подготовка кораблей в интерактивном режиме
    # ToDo: пока не работет
    def init_ships(self, board_size: int, ships_quantity: dict) -> list[Ship]:
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
            print(f"Ход игрока '{self.name}'")
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

            shot = Point(x, y)
            if not shot.in_board(self.board):
                print_error(f"Вы стреляете в пустоту! Координаты ({x}, {y}) находятся за пределами "
                            f"игрового поля {self.board.size}x{self.board.size}")
                print("Попробуйте еще раз")
                continue
            else:
                return GameEvent(GameEvent.Event_Shot, self, shot)

    def congrats(self) -> str:
        text = f"{self.name} поздравляю!\nВы победили!!"
        return text


# класс компьютерного игрока
class ComputerPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.__possible_moves = []

    # Автоматическая генерация кораблей случайным образом
    def init_ships(self, board_size: int, ships_quantity: dict) -> list[Ship]:
        tmp_board = [[SeaBattleGameBoard.Fog_Of_War for _ in range(board_size)] for _ in range(board_size)]
        ships = []

        for ship_size in ships_quantity.keys():
            # print(f"Генерим {ships_quantity[ship_size]} кораблей длиной {ship_size}:")
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
                            # print(f">> Выбираем {num} из {len(list_of_candidates)}: {ship}")
                            ships.append(ship)
                            for p in ship.body:
                                tmp_board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Ship_Body
                            for p in ship.nearby:
                                if p.x in range(1, board_size + 1) and p.y in range(1, board_size + 1):
                                    tmp_board[p.x - 1][p.y - 1] = SeaBattleGameBoard.Sea_Spot
                            ship_found = True
                    except IndexError as e:
                        continue

        return ships

    def generate_moves(self) -> None:
        for y in rnd.sample(range(self.board.size), self.board.size):
            for x in rnd.sample(range(self.board.size), self.board.size):
                self.__possible_moves.append(Point(x + 1, y + 1))

    def get_move(self) -> GameEvent:
        _ = input(f"Ход компьютера '{self.name}'\nНажмите [Enter] для продолжения...")
        i = rnd.randint(0, len(self.__possible_moves) - 1)
        shot = self.__possible_moves[i]
        self.__possible_moves.pop(i)
        print(f"{self.name} стреляет {shot}")
        return GameEvent(GameEvent.Event_Shot, self, shot)

    @property
    def board(self) -> SeaBattleGameBoard:
        return self.__board

    @board.setter
    def board(self, board) -> None:
        self.__board = board
        self.generate_moves()

    def congrats(self) -> str:
        if self.enemy.__class__.__name__ == HumanPlayer:
            text = f"Увы, {self.enemy.name}, вы проиграли...\nЗаходите еще!"
        else:
            text = f"Победил {self.name}\nЭто ж компьютер, что с него взять..."
        return text


# ---------------------------------
# класс логики игры "Морской бой"
class SeaBattleGameLogic:
    Ships_Quantity = {
        3: 1,
        2: 2,
        1: 4
    }

    def __init__(self, size: int, player1: Player, player2: Player) -> None:
        self.__board_size = size
        self.__player1 = player1
        self.__player2 = player2
        self.__player1.enemy = self.__player2
        self.__player2.enemy = self.__player1
        self.__player1.board = SeaBattleGameBoard(size, self.__player1.init_ships(size, self.Ships_Quantity))
        self.__player2.board = SeaBattleGameBoard(size, self.__player2.init_ships(size, self.Ships_Quantity))

    @property
    def player1(self) -> Player:
        return self.__player1

    @property
    def player2(self) -> Player:
        return self.__player2

    def process_event(self, event: GameEvent) -> None:
        try:
            if event.type == GameEvent.Event_Shot:
                if event.player.enemy.board.incoming_shot(event.data):
                    event.player.last_shot_success = True
                else:
                    event.player.last_shot_success = False
                    event.player.enemy.last_shot_success = True
        except ValueError:
            print_error("Вы сюда уже стреляли!")


if __name__ == "__main__":
    board_size = 6
    user = ComputerPlayer('Компутер')
    user.board = SeaBattleGameBoard(board_size, user.init_ships())
    print(user.name)
    print(user.board)
