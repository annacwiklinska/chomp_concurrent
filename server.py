import random
import socket
import threading
import time

from board import Board


def sleep_after(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(0.1)
        return result

    return wrapper


class ChompServer:
    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.clients = []
        self.board = Board()
        self.current_player = None
        self.lock = threading.Lock()
        self.want_to_play_again = []

    # @sleep_after
    def broadcast(self, message):
        for client in self.clients:
            client.send(message.encode())

    # @sleep_after
    def broadcast_board(self):
        for client in self.clients:
            client.send(("BOARD " + str(self.board)).encode())

    # @sleep_after
    def send_message_to(self, message, client):
        client.send(message.encode())

    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024).decode()
                if not data:
                    self.remove_client(client)
                    time.sleep(0.1)
                    self.broadcast("DISCONNECTED")
                    break

                if data.startswith("SIZE"):
                    _, width, height = data.split(" ")
                    self.board = Board(int(width), int(height))
                    self.broadcast_board()
                    time.sleep(0.1)
                    self.send_message_to("YOUR_TURN", client)

                if data.startswith("MOVE"):
                    _, move = data.split(" ")
                    print(move)
                    if self.current_player == client and self.board.is_valid_move(move):
                        self.board.make_move(move)
                        self.broadcast_board()
                        if self.board.is_game_over():
                            self.broadcast("GAME_OVER")
                            time.sleep(0.1)
                            self.send_message_to("LOST", self.current_player)
                            self.send_message_to(
                                "WIN",
                                self.clients[0]
                                if self.current_player == self.clients[1]
                                else self.clients[1],
                            )
                        else:
                            self.current_player = (
                                self.clients[1]
                                if self.current_player == self.clients[0]
                                else self.clients[0]
                            )
                            self.send_message_to("YOUR_TURN", self.current_player)
                    else:
                        client.send("INVALID".encode())

                if data.startswith("AGAIN"):
                    _, answer = data.split(" ")
                    if answer == "YES":
                        self.want_to_play_again.append(client)
                        if len(self.want_to_play_again) == 2:
                            self.board = Board()
                            # self.broadcast_board()
                            self.current_player = random.choice(self.clients)
                            self.broadcast("GAME_START")
                            time.sleep(0.1)
                            self.send_message_to(
                                "CHOOSE_BOARD_SIZE", self.current_player
                            )
                            self.want_to_play_again = []
                        elif len(self.want_to_play_again) == 1:
                            self.send_message_to("WAIT", client)
                    else:
                        self.remove_client(client)
                        break
            except Exception as e:
                print(e)
                self.remove_client(client)
                break

    def remove_client(self, client):
        with self.lock:
            if client in self.clients:
                self.clients.remove(client)
                print(f"Disconnected {client}")

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected with {addr}")
            self.clients.append(client_socket)

            if len(self.clients) == 1:
                self.send_message_to("WAIT", client_socket)

            if len(self.clients) == 2:
                self.current_player = random.choice(self.clients)
                self.broadcast("GAME_START")
                time.sleep(0.1)
                self.send_message_to("CHOOSE_BOARD_SIZE", self.current_player)
                self.want_to_play_again = []

            elif len(self.clients) > 2:
                self.send_message_to("FULL", client_socket)
                self.remove_client(client_socket)
                continue

            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            client_thread.start()


if __name__ == "__main__":
    server = ChompServer()
    server.start()
