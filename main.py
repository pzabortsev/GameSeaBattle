from gameLogic import Point, GameEvent, Ship, GameBoard, GameLogicSeaBattle


# -----------------------------------------
class ConsoleGameGui:
    def __init__(self, board_size, logic) -> None:
        self.board_size = board_size
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
        marks = self.logic.get_board()
        for i in range(len(marks)):
            print(f"{i}. [{marks[i].get_pos().x}, {marks[i].get_pos().y}, {marks[i].get_width()}, {marks[i].get_height()}]")

        score = self.logic.get_score()
        accuracity = self.logic.get_accuracity()
        print(f'score:{score}')
        print(f'accuracity:{accuracity:.0f}%')

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
