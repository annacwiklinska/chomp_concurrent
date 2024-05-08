class Game:
    def __init__(self, board, client1, client2):
        self.board = board
        self.clients = [client1, client2]

    def play(self):
        for client in self.clients:
            client.send_board(self.board.fields)

        while True:
            for client in self.clients:
                move = client.get_move()
                self.board.make_move(move)

                if self.board.is_game_over():
                    for client in self.clients:
                        client.send_message("Game over!")
                    break

                for client in self.clients:
                    client.send_board(self.board.fields)

        for client in self.clients:
            client.close()
