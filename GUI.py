import threading
import tkinter as tk

from client import Client


class GUI:
    def __init__(self):
        self.client = Client()

        self.root = tk.Tk()
        self.root.title("Chomp")
        self.root.geometry("300x300")

        self.home_screen()

    def home_screen(self):
        self.label = tk.Label(self.root, text="Press button to start game")
        self.label.pack()

        self.button = tk.Button(self.root, text="Start game", command=self.start_game)
        self.button.pack()

    def start_game(self):
        try:
            client_thread = threading.Thread(target=self.client_thread)
            client_thread.start()

            self.label.config(text="Client started successfully.")
            self.button.config(state=tk.DISABLED)
        except ConnectionRefusedError:
            self.label.config(text="Server is not running. Please try again later.")
            self.button.config(text="Quit", command=self.root.quit)

    def process_data_override(self, data):
        if data == "FULL":
            self.label.config(text="Game is full. Try again later.")
            self.button.config(text="Quit", command=self.root.quit)
        elif data == "WAIT":
            self.label.config(text="Waiting for the second player to join...")
        elif data == "GAME_START":
            self.label.config(text="Game started!")
        elif data.startswith("BOARD"):
            self.print_game_board(data)
        elif data == "YOUR_TURN":
            self.make_move()
        elif data == "CHOOSE_BOARD_SIZE":
            self.choose_board_size()
        elif data == "GAME_OVER":
            self.label.config(text="Game over!")
        elif data == "LOST":
            self.label.config(text="You lost!")
            self.close()
        elif data == "WIN":
            self.label.config(text="You won!")
            self.close()
        elif data == "INVALID":
            self.label.config(text="Invalid move! Try again.")
            self.make_move()

    def choose_board_size(self):
        self.label.config(text="Enter board size (width,height): ")
        self.entry = tk.Entry(self.root)
        self.entry.pack()

        self.button.config(text="Submit", command=self.send_board_size, state=tk.NORMAL)
        # self.button.pack()

    def send_board_size(self):
        size = self.entry.get()
        while not size.replace(",", "").isdigit():
            self.label.config(
                text="Invalid input. Please enter two numerical values separated by a comma."
            )
            size = self.entry.get()
        message = f"SIZE {size.replace(',', ' ')}"
        self.client.client_socket.send(message.encode())

    def print_game_board(self, data):
        self.label.config(text="Game board:")
        _, board = data.split(" ")
        self.label.config(text=board)

    def make_move(self):
        self.entry.destroy()

        self.label = tk.Label(self.root)
        self.label.config(text="Your turn.")
        self.label.pack()

        self.label = tk.Label(self.root)
        self.label.config(text="Enter move (row,col): ")
        self.label.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()

        self.button = tk.Button(self.root)
        self.button.config(text="Submit", command=self.send_move, state=tk.NORMAL)
        self.button.pack()

    def send_move(self):
        move = self.entry.get()
        message = f"MOVE {move}"
        self.client.client_socket.send(message.encode())

    def client_thread(self):
        self.client.connect()
        self.client.receive()

    def run(self):
        self.root.mainloop()


gui = GUI()
gui.client.process_data = gui.process_data_override
gui.run()
gui.client.close()
