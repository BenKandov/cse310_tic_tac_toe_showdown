from socketserver import *
from threading import *


class Player:
    def __init__(self, player_name, fd):
        self.aval = True
        self.player_name = player_name
        self.fd = fd

    def set_aval(self, boo):
        self.aval = boo

    def set_tic(self, tic):
        self.tic = tic


class Game:
    def __init__(self, game_id, player_x, player_o):
        self.game_id = game_id
        self.player_x = player_x
        player_x.set_tic("X")
        self.player_o = player_o
        player_o.set_tic("O")
        self.turn = player_x
        self.board_array = []
        for y in range(3):
            self.board_array.append(['.' for i in range(3)])


# ids will be generated from this incrementing game_counter
game_counter = 0

# variables for keeping track of game state


player_list = []
games_list = []


def start_game():
    pass


def end_game():
    pass


def search_for_player_name(player_name):
    global player_list
    for player in player_list:
        if player.player_name == player_name:
            return player
    return None


def exit(player_name):
    global player_list
    if search_for_player_name(player_name) is not None:
        player_list.remove(search_for_player_name(player_name))
    else:
        # send this message to client
        print("Error: This player is not currently logged in")


def login(player_name, fd):
    global player_list
    if search_for_player_name(player_name) is None:
        player = Player(player_name, fd)
        player_list.append(player)
        return True
    else:
        # send this message to client
        return False


def who_command(player_name):
    global player_list
    for player in player_list:
        if player.player_name != player_name:
            print(player.player_name)


# variables for keeping track of game state




def print_board(board_array):
    for row in board_array:
        for item in row:
            print(item, end='')
        print('')


# invalid moves should be checked before calling this method
# perhaps later check if spot has already been taken and return error to client
# definitely check whose turn it is and return error if applicable
def move_on_board(board_array, n: int, tac: str):
    if n < 1 or n > 9:
        return False
    row = 1
    if n > 3:
        diff = n - 3
        row += 1
        if diff > 3:
            diff -= 3
            row += 1
        n = diff
    if board_array[row-1][n-1] != '.':
        return False
    board_array[row - 1][n - 1] = tac
    return True


# returns 1 for player X and 2 for player O, 0 for neither
def check_win_conditions(board_array):
    # check left diagonal win
    if (board_array[0][0] == board_array[1][1]) and \
            (board_array[1][1] == board_array[2][2]):
        if "X" in board_array[0][0]:
            return 2
        else:
            return 1
    # check right diagonal win
    if (board_array[0][2] == board_array[1][1]) and \
            (board_array[1][1] == board_array[2][0]):
        if "X" in board_array[0][2]:
            return 2
        else:
            return 1

    # check for row wins
    for row in board_array:
        if (row[0] == row[1]) and \
                (row[1] == row[2]):
            if "X" in row[0]:
                return 2
            elif "O" in row[0]:
                return 1

    # check for column wins
    for i in range(0, 3):
        if (board_array[0][i] == board_array[1][i]) and \
                (board_array[1][i] == board_array[2][i]):
            if "X" in board_array[0][i]:
                return 2
            elif "O" in board_array[0][i]:
                return 1
    return 0


# PROTOCOL CONSTANTS

bad_format = "400 ERROR\nMALFORMED MESSAGE\r\n"
name_taken = "400 ERROR\nUsername is already taken\r\n"
success = "200 OK\nSUCCESS\r\n"
who_success = "200 OWH\nSUCCESS\r\n "
games_success = "200 SEMAG\nSUCCESS\r\n "
carriage = "\r\n"
newline = '\n'
player_one_intro = 'Player X is: '
player_two_intro = 'Player O is: '
invalid_player_name = "400 ERROR\nTHIS PLAYER IS NOT LOGGED IN\r\n"
busy_player_name = "400 ERROR\nTHIS PLAYER IS BUSY\r\n"
game_starting = "200 YALP\nYou have entered into a game with "
icon_assignment = "200 ICON\nYour icon will be "
o_icon = "O and you will move second."
x_icon = "X and you will move first."
invalid_move = "400 ERROR\nINVALID MOVE\r\n"
wrong_turn = "400 ERROR\nNOT YOUR TURN\r\n"
good_move = "200 ECALP\n"
good_opponent_move = "200 OECALP\n"
x = 'X'
o = 'O'
dot = '.'


# PROTOCOL CONSTANTS

class ThreadedTCPCommunicationHandler(BaseRequestHandler):
    def handle(self):
        global player_list
        global games_list
        global game_counter
        player_name = ""
        logged_in = False
        in_lobby = False
        in_game = False
        current_game = None
        while 1:
            if not logged_in:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if 'LOGIN ' in string_message:
                    return_str = string_message.split("LOGIN ")[1]
                    if '\r\n' in return_str:
                        username = return_str.split("\r\n")[0]
                        if login(username, self.request):
                            self.request.sendall(success.encode())
                            player_name = username
                            logged_in = True
                            in_lobby = True
                        else:
                            self.request.sendall(name_taken.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                else:
                    self.request.sendall(bad_format.encode())
            elif in_lobby and search_for_player_name(player_name).aval:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if "WHO" in string_message:
                    return_str = string_message.split("WHO")[1]
                    if '\r\n' in return_str:
                        self.request.sendall(who_success.encode())
                        for player in player_list:
                            if player.player_name != player_name:
                                self.request.sendall(player.player_name.encode())
                                self.request.sendall(newline.encode())
                        self.request.sendall(carriage.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                elif "PLAY " in string_message:
                    return_str = string_message.split("PLAY ")[1]
                    if '\r\n' in return_str:
                        username = return_str.split("\r\n")[0]
                        if search_for_player_name(username) is not None:
                            player = search_for_player_name(username)
                            if player.aval:
                                new_game = Game(game_counter, search_for_player_name(player_name), player)
                                games_list.append(new_game)
                                search_for_player_name(player_name).set_aval(False)
                                search_for_player_name(player_name).set_tic('X')
                                self.request.sendall(game_starting.encode())
                                self.request.sendall(username.encode())
                                self.request.sendall(newline.encode())
                                self.request.sendall(icon_assignment.encode())
                                self.request.sendall(x_icon.encode())
                                self.request.sendall(carriage.encode())
                                player.set_aval(False)
                                player.set_tic('O')
                                player.fd.sendall(game_starting.encode())
                                player.fd.sendall(player_name.encode())
                                player.fd.sendall(newline.encode())
                                player.fd.sendall(icon_assignment.encode())
                                player.fd.sendall(o_icon.encode())
                                player.fd.sendall(carriage.encode())
                                game_counter += 1
                                in_game = True
                                in_lobby = False
                                current_game = new_game
                            else:
                                self.request.sendall(busy_player_name.encode())
                        else:
                            self.request.sendall(invalid_player_name.encode())
                    else:
                        self.request.sendall(bad_format.encode())

                elif "GAMES" in string_message:
                    return_str = string_message.split("GAMES")[1]
                    if '\r\n' in return_str:
                        self.request.sendall(games_success.encode())
                        for game in games_list:
                            self.request.sendall(player_one_intro.encode())
                            self.request.sendall(game.player_x.encode())
                            self.request.sendall(player_two_intro.encode())
                            self.request.sendall(game.player_o.encode())
                            self.request.sendall(newline.encode())
                        self.request.sendall(carriage.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                else:
                    self.request.sendall(bad_format.encode())
            elif in_game or (
                            search_for_player_name(player_name) is not None and search_for_player_name(
                        player_name).aval is False):
                if current_game is None:
                    in_game = True
                    in_lobby = False
                    for game in games_list:
                        if game.player_o == search_for_player_name(player_name):
                            current_game = game
                            break
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")

                if "PLACE " in string_message:
                    return_str = string_message.split("PLACE")[1]
                    if current_game.turn is not search_for_player_name(player_name):
                        self.request.sendall(wrong_turn.encode())
                    elif "\r\n" in return_str:
                        n = return_str.split("\r\n")[0]
                        if move_on_board(current_game.board_array, int(n), search_for_player_name(player_name).tic):
                            self.request.sendall(good_move.encode())
                            for row in current_game.board_array:
                                for item in row:
                                    self.request.sendall(item.encode())
                                self.request.sendall(newline.encode())
                            self.request.sendall(carriage.encode())
                            if current_game.turn is current_game.player_x:
                                current_game.player_o.fd.sendall(good_opponent_move.encode())
                                for row in current_game.board_array:
                                    for item in row:
                                        current_game.player_o.fd.sendall(item.encode())
                                    current_game.player_o.fd.sendall(newline.encode())
                                current_game.player_o.fd.sendall(carriage.encode())
                                current_game.turn = current_game.player_o
                            else:
                                current_game.player_x.fd.sendall(good_opponent_move.encode())
                                for row in current_game.board_array:
                                    for item in row:
                                        current_game.player_x.fd.sendall(item.encode())
                                    current_game.player_x.fd.sendall(newline.encode())
                                current_game.player_x.fd.sendall(carriage.encode())
                                current_game.turn = current_game.player_x
                            # check win conditions and end game if necessary
                            check_win_conditions(current_game.board_array)
                        else:
                            self.request.sendall(invalid_move.encode())
                    else:
                        self.request.sendall(bad_format.encode())

                else:
                    self.request.sendall(bad_format.encode())


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 1234
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPCommunicationHandler)
    server.serve_forever()
