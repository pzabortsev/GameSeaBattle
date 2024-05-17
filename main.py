from gameLogic import GameEvent, SeaBattleGameBoard, SeaBattleGameLogic, HumanPlayer, ComputerPlayer


# -----------------------------------------
class ConsoleGameGui:
    Visual = ['○', '◌', '■', '◦', '▪', 'X']

    def __init__(self, size, logic) -> None:
        self.__board_size = size
        self.logic = logic

    # Генератор потока событий GameEvent для основноего цикла игры
    def get_event(self) -> list[GameEvent]:
        while True:
            for player in [self.logic.player1, self.logic.player2]:
                while player.last_shot_success:
                    try:
                        yield player.get_move()
                    except KeyboardInterrupt:
                        yield GameEvent(GameEvent.Event_Quit)

                    if player.is_winner:
                        yield GameEvent(GameEvent.Event_Win, player)

    def process_event(self, event):
        self.logic.process_event(event)

    def draw(self):
        # Вывод заголовка с (1) именами игроков, (2) количеством живых кораблей и (3) номерами столбцов
        print()
        print("{:<15}  :  {:>15}".format(self.logic.player1.name, self.logic.player2.name))
        print("{:<15}  :  {:>15}".format("Кораблей: " + str(self.logic.player1.board.alive_ships_count),
                                         "Кораблей: " + str(self.logic.player2.board.alive_ships_count)))
        row = ' '
        for x in range(self.board_size):
            row = row + ' ' + str(x + 1)
        print("{:<15}     {:>15}".format(row, row))

        # Построчный вывод на консоль двух полей с номерами строк (координата y) в начале каждой строки
        # Левое поле - поле игрока player1
        # Правое поле - поле игрока player2
        # ToDo: оптимизировать, упростить
        for y in range(self.board_size):
            rows = []
            for player in [self.logic.player1, self.logic.player2]:
                row = str(y + 1)
                for x in range(self.board_size):
                    if player.__class__.__name__ == player.enemy.__class__.__name__ == 'HumanPlayer':
                        row = row + ' ' + self.Visual[player.board.enemy_shots[x][y]]
                    elif player.__class__.__name__ == player.enemy.__class__.__name__ == 'ComputerPlayer':
                        if (player.board.enemy_shots[x][y] in
                                [SeaBattleGameBoard.Fog_Of_War, SeaBattleGameBoard.Ship_Neighbor]):
                            row = row + ' ' + self.Visual[player.board.board[x][y]]
                        else:
                            row = row + ' ' + self.Visual[player.board.enemy_shots[x][y]]
                    elif player.__class__.__name__ == 'HumanPlayer' and player.enemy.__class__.__name__ == 'ComputerPlayer':
                        if (player.board.enemy_shots[x][y] in
                                [SeaBattleGameBoard.Fog_Of_War, SeaBattleGameBoard.Ship_Neighbor]):
                            row = row + ' ' + self.Visual[player.board.board[x][y]]
                        else:
                            row = row + ' ' + self.Visual[player.board.enemy_shots[x][y]]
                    else:
                        row = row + ' ' + self.Visual[player.board.enemy_shots[x][y]]
                rows.append(row)
            print("{:<15}     {:>15}".format(rows[0], rows[1]))

    def run(self):
        for event in self.get_event():
            if event.type == GameEvent.Event_Quit:
                print("Bye-bye!")
                break
            elif event.type == GameEvent.Event_Win:
                print()
                print(event.player.congrats())
                break
            else:
                self.process_event(event)

            self.draw()

    @property
    def board_size(self) -> int:
        return self.__board_size


# --------------------------------------------
if __name__ == "__main__":
    board_size = 6
    print("\nДобро пожаловать в игру «Морской бой»!\n")
    str_ = input("Назовите имя первого игрока (оставьте имя пустым, если играть будет Компьютер): ")
    player1 = HumanPlayer(str_) if str_ else ComputerPlayer("Комп 1")

    str_ = input("Назовите имя второго игрока (оставьте имя пустым, если играть будет Компьютер): ")
    player2 = HumanPlayer(str_) if str_ else ComputerPlayer("Комп 1")
    if player1.__class__.__name__ == 'ComputerPlayer' and player2.__class__.__name__ == 'ComputerPlayer':
        player2.name = "Комп 2"

    gui = ConsoleGameGui(board_size, SeaBattleGameLogic(board_size, player1, player2))
    gui.draw()
    gui.run()
