class Board:
    def __init__(self, width=5, height=4):
        self.width = min(width, 20)
        self.height = min(height, 20)
        self.fields = [[True for _ in range(width)] for _ in range(height)]

    def __str__(self):
        return "\n".join(
            ["".join(["#" if field else "." for field in row]) for row in self.fields]
        )

    def is_game_over(self):
        return self.fields[0][0] is False

    def is_valid_move(self, move):
        try:
            row, col = move.split(",")
            row, col = int(row), int(col)
            row -= 1
            col -= 1
            if row < 0 or row >= self.height or col < 0 or col >= self.width:
                print("here1")
                return False
            if self.fields[row][col] is False:
                print("here2")
                return False
            return True
        except ValueError:
            print("Value error")
            return False

    def make_move(self, move):
        row, col = move.split(",")
        row, col = int(row), int(col)
        self.fields[row - 1][col - 1] = False
        for i in range(row - 1, self.height):
            for j in range(col - 1, self.width):
                self.fields[i][j] = False
