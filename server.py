
from socketserver import *
from threading import *

class Player:
    def __init__(self, player_name):
        self.aval = True
        self.player_name = player_name

    def set_aval(self, boo):
        self.aval = boo

    def set_tic(self, tic):
        self.tic = tic


class Game:
    def __init__(self, game_id, player_x, player_o):
        self.game_id = game_id
        self.player_x = player_x
        player_x.set_tic("X ")
        self.player_o = player_o
        player_o.set_tic("O ")


# ids will be generated from this incrementing game_counter
game_counter = 0

# variables for keeping track of game state

board_array = [['. ' for x in range(3)] for y in range(3)]
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


def login(player_name):
    global player_list
    if search_for_player_name(player_name) is None:
        player = Player(player_name)
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

board_array = [['. ' for x in range(3)] for y in range(3)]



def print_board():
    global board_array
    for row in board_array:
        for item in row:
            print(item, end='')
        print('')


# invalid moves should be checked before calling this method
# perhaps later check if spot has already been taken and return error to client
# definitely check whose turn it is and return error if applicable
def move_on_board(n: int, tac: str):
    global board_array
    row = 1
    if n > 3:
        diff = n - 3
        row += 1
        if diff > 3:
            diff -= 3
            row += 1
        n = diff
    board_array[row - 1][n - 1] = tac


# returns 1 for player X and 2 for player O, 0 for neither
def check_win_conditions():
    global board_array

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


move_on_board(3, '0 ')
move_on_board(5, '0 ')
move_on_board(7, '0 ')

print_board()
if check_win_conditions() == 2:
    print("O player wins!")
elif check_win_conditions() == 1:
    print("X player wins!")



#PROTOCOL CONSTANTS

bad_format = "400 ERROR\nMALFORMED MESSAGE\r\n"
name_taken = "400 ERROR\nUsername is already taken\r\n"
success = "200 OK\nSUCCESS\r\n"
who_success = "200 OWH\nSUCCESS\r\n "
carriage = "\r\n"
#PROTOCOL CONSTANTS

class ThreadedTCPCommunicationHandler(BaseRequestHandler):

    def handle(self):
        global player_list
        player_name = ""
        logged_in = False
        in_lobby = False
        while(1):
            if not logged_in:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if 'LOGIN ' in string_message:
                    return_str = string_message.split("LOGIN ")[1]
                    if '\r\n' in return_str:
                        username = return_str.split("\r\n")[0]
                        if login(username):
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
            elif in_lobby:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if "WHO" in string_message:
                    return_str = string_message.split("WHO")[1]
                    if '\r\n' in return_str:
                        self.request.sendall(who_success.encode())
                        for player in player_list:
                            if player.player_name != player_name:
                                self.request.sendall(player.player_name.encode())
                                self.request.sendall(carriage.encode())

                    else:
                        self.request.sendall(bad_format.encode())
                elif "PLAY" in string_message:
                    pass
                elif "GAMES" in string_message:
                    pass
                else:
                    self.request.sendall(bad_format.encode())



class ThreadedTCPServer(ThreadingMixIn,TCPServer):
    pass

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 1234
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPCommunicationHandler)
    server.serve_forever()


