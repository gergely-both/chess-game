from models import Board, Game
import tkinter as tk


def user_interaction(board_instance, game_instance):
    board_instance.canvas.bind(
        "<Button-1>", lambda event: board_instance.click(event, game_instance)
    )


if __name__ == "__main__":
    gui = tk.Tk()

    board = Board(gui)
    game = Game()
    user_interaction(board, game)

    gui.mainloop()
