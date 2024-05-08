import socket


class Client:
    def __init__(self, server_address="localhost", server_port=5555):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.server_address, self.server_port))
        print("Connected to the server.")

    def receive(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    self.process_data(data)
            except Exception as e:
                print(e)
                print("Connection lost.")
                self.client_socket.close()
                exit()

    def process_data(self, data):
        if data == "FULL":
            print("Game is full. Try again later.")
            exit()
        elif data == "WAIT":
            print("Waiting for the second player to join...")
        elif data == "GAME_START":
            print("Game started!")
        elif data.startswith("BOARD"):
            self.print_game_board(data)
        elif data == "YOUR_TURN":
            print("Your turn.")
            self.make_move()
        elif data == "CHOOSE_BOARD_SIZE":
            self.choose_board_size()
        elif data == "GAME_OVER":
            print("Game over!")
        elif data == "LOST":
            print("You lost!")
            self.close()
            exit()
        elif data == "WIN":
            print("You won!")
            self.close()
            exit()
        elif data == "INVALID":
            print("Invalid move! Try again.")
            self.make_move()

    def choose_board_size(self):
        size = input("Enter board size (width,height): ")
        while not size.replace(",", "").isdigit():
            print(
                "Invalid input. Please enter two numerical values separated by a comma."
            )
            size = input("Enter board size: ")
        message = f"SIZE {size.replace(',', ' ')}"
        self.client_socket.send(message.encode())

    def print_game_board(self, data):
        print("Game board:")
        _, board = data.split(" ")
        print(board)

    def send_move(self, move):
        message = f"MOVE {move}"
        self.client_socket.send(message.encode())

    def close(self):
        self.client_socket.close()
        print("Connection closed.")

    def make_move(self):
        move = input("Enter your move (row,col): ")
        while not move.replace(",", "").isdigit():
            print(
                "Invalid input. Please enter two numerical values separated by a comma."
            )
            move = input("Enter your move: ")
        self.send_move(move)


if __name__ == "__main__":
    client = Client()
    client.connect()
    client.receive()
    client.close()