from gameLogic import Point, GameEvent, Ship, GameBoard, GameLogicSeaBattle


# -----------------------------------------
class ConsoleGameGui:
    Ship_Body = '■'
    Sea_Spot = '.'

    def __init__(self, size, logic) -> None:
        self.board_size = size
        self.logic = logic

    def get_event(self) -> GameEvent:
        while True:
            yield GameEvent(GameEvent.Event_Tick, None)

            str_ = input("Введите координаты (X Y), куда вы хотите выстрелить, разделенные пробелом (q для выхода): ")

            if str_ == '':
                print("Все-таки введите что-нибудь...")
                continue

            if str_[0] == 'q':
                print("Bye-bye!")
                yield GameEvent(GameEvent.Event_Quit, None)
                break

            x, y = map(int, str_.split())
            print(f"Вы ввели {x}, {y}")
            yield GameEvent(GameEvent.Event_Hit, Point(x, y))

    def process_event(self, event):
        self.logic.process_event(event)

    def draw(self):
        user_board = self.logic.get_user_board()



    def run(self):
        for event in self.get_event():
            if event.type == GameEvent.Event_Quit:
                break
            else:
                self.process_event(event)

            self.draw()


# --------------------------------------------
if __name__ == "__main__":
    board_size = 6
    gui = ConsoleGameGui(board_size, GameLogicSeaBattle(board_size))
    gui.run()
