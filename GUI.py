import threading

import pygame

from client import Client

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 800  # Adjusted for a centered 20x20 board
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chomp")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)  # Chocolate color
GRAY = (200, 200, 200)

# Define fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Define game states
STATE_HOME = 0
STATE_WAITING = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3
STATE_CHOOSING_BOARD = 4

# Tile dimensions
TILE_SIZE = 30
BOARD_SIZE = 20
BOARD_PIXEL_SIZE = TILE_SIZE * BOARD_SIZE


class Tile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.default_color = BROWN
        self.hover_color = RED
        self.current_color = self.default_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)  # Border

    def handle_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.default_color

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # React to tile being clicked
                # Add your code here
                pass


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.default_color = GRAY
        self.hover_color = WHITE
        self.current_color = self.default_color

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)  # Border
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        # Center the button horizontally on the screen
        text_rect.centerx = surface.get_rect().centerx
        text_surf.centerx = surface.get_rect().centerx
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.default_color


class GUI:
    def __init__(self):
        self.client = Client()
        self.state = STATE_HOME
        self.message = "Press SPACE to start the game."
        self.board = [
            [
                Tile(
                    x * TILE_SIZE + (screen_width - BOARD_PIXEL_SIZE) // 2,
                    y * TILE_SIZE + 100,
                )
                for x in range(BOARD_SIZE)
            ]
            for y in range(BOARD_SIZE)
        ]
        self.input_active = False
        self.input_text = ""
        self.default_button = Button(20, 60, 120, 40, "Default 4x5")

        # Start Pygame clock
        self.clock = pygame.time.Clock()

    def draw_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def start_game(self):
        try:
            self.client.connect()
            client_thread = threading.Thread(target=self.client_thread)
            client_thread.start()
            self.message = "Client started successfully."
            self.state = STATE_WAITING
        except ConnectionRefusedError:
            self.message = "Server is not running. Please try again later."

    def process_data_override(self, data):
        if data == "FULL":
            self.message = "Game is full. Try again later."
            self.state = STATE_GAME_OVER
        elif data == "WAIT":
            self.message = "Waiting for the second player to join..."
        elif data == "GAME_START":
            self.message = "Game started!"
            self.state = STATE_PLAYING
        elif data.startswith("BOARD"):
            self.board = data.split(" ")[1]
        elif data == "YOUR_TURN":
            self.message = "Your turn. Enter move (row,col):"
            self.input_active = True
        elif data == "CHOOSE_BOARD_SIZE":
            self.message = "Choose board size or use default."
            self.state = STATE_CHOOSING_BOARD
            self.input_active = True
        elif data == "GAME_OVER":
            self.message = "Game over!"
            self.state = STATE_GAME_OVER
        elif data == "LOST":
            self.message = "You lost!"
            self.state = STATE_GAME_OVER
        elif data == "WIN":
            self.message = "You won!"
            self.state = STATE_GAME_OVER
        elif data == "INVALID":
            self.message = "Invalid move! Try again."

    def send_board_size(self, size):
        message = f"SIZE {size}"
        self.client.client_socket.send(message.encode())
        self.input_text = ""
        self.input_active = False
        self.state = STATE_WAITING

    def send_move(self):
        message = f"MOVE {self.input_text}"
        self.client.client_socket.send(message.encode())
        self.input_text = ""
        self.input_active = False

    def client_thread(self):
        self.client.receive()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_HOME and event.key == pygame.K_SPACE:
                    self.start_game()
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.state == STATE_CHOOSING_BOARD:
                            self.send_board_size(self.input_text.replace(",", " "))
                        elif self.state == STATE_PLAYING:
                            self.send_move()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.state == STATE_CHOOSING_BOARD:
                    if self.default_button.is_clicked(pos):
                        self.send_board_size("4 5")
                if self.state == STATE_PLAYING:
                    for row in self.board:
                        for tile in row:
                            if tile.rect.collidepoint(pos):
                                row, col = (
                                    tile.rect.y // TILE_SIZE - 3,
                                    tile.rect.x // TILE_SIZE
                                    - (screen_width - BOARD_PIXEL_SIZE)
                                    // TILE_SIZE
                                    // 2,
                                )
                                self.input_text = f"{row},{col}"
                                self.send_move()
                                break
        return True

    def draw_board(self, surface):
        for row in self.board:
            for tile in row:
                tile.draw(surface)

    def run(self):
        running = True
        try:
            while running:
                running = self.handle_events()

                screen.fill(WHITE)
                self.draw_text(self.message, font, BLACK, screen, 20, 20)
                if self.state == STATE_CHOOSING_BOARD:
                    self.default_button.draw(screen, font)
                    self.draw_board(screen)
                if self.input_active:
                    self.draw_text(self.input_text, font, RED, screen, 20, 100)
                pygame.display.flip()

                self.clock.tick(30)
        except Exception as e:
            self.message = e
            pygame.display.flip()
        finally:
            pygame.quit()
            self.client.close()


gui = GUI()
gui.client.process_data = gui.process_data_override
gui.run()
