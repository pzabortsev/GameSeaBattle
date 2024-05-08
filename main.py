from tools import Pos


class Ship:
    def __init__(self, *points):
        self.__body = []
        self.__size = 0
        for pos in points:
            self.__body.append(pos)
            self.__size += 1

    def __str__(self):
        return f"The Ship is {self.__size} size"

class GameBoard:
    def __init__(self, *ships):
        self.__ships = []
        self.__ships_alive = 0
        for ship in ships:
            self.__ships.append(ship)
            self.__ships_alive += 1

    @property
    def ships_alive(self):
        return self.__ships_alive


if __name__ == "__main__":
    ship_1 = Ship(Pos(1, 1), Pos(1, 2))
    ship_2 = Ship(Pos(5, 2), Pos(5, 3), Pos(5, 4))
    ship_3 = Ship(Pos(3,3))
    ship_4 = Ship(Pos(6, 6), Pos(5, 6))

    print(ship_1)
    print(ship_2)
    print(ship_3)
    print(ship_4)

    game = GameBoard(ship_1, ship_2, ship_3, ship_4)
    print(f"На поле {game.ships_alive} живых кораблей")