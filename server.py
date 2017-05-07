from socketserver import *



#This is a class definition for the player object, which keeps state information
class Player:
    def __init__(self, player_name, fd):
        self.aval = True
        self.player_name = player_name
        self.fd = fd
        self.auto = False
        self.current_game = None
        self.turn = False

    def set_auto(self):
        self.auto = True

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

# variables for keeping track of game state and games/players running
player_list = []
games_list = []
auto_player_queue = []


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

def auto_login(player_name, fd):
    global auto_player_queue
    if search_for_player_name(player_name) is None:
        player = Player(player_name, fd)
        player.set_auto()
        auto_player_queue.append(player)
        player_list.append(player)
        return True
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
        elif "O" in board_array[0][0]:
            return 1
    # check right diagonal win
    if (board_array[0][2] == board_array[1][1]) and \
            (board_array[1][1] == board_array[2][0]):
        if "X" in board_array[0][2]:
            return 2
        elif "O" in board_array[0][2]:
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
who_success = "200 OHW\n"
games_success = "200 SEMAG\n"
carriage = "\r\n"
newline = '\n'
comma = ','
player_one_intro = 'Player X is: '
player_two_intro = 'Player O is: '
invalid_player_name = "400 ERROR\nTHIS PLAYER IS NOT LOGGED IN\r\n"
busy_player_name = "400 ERROR\nTHIS PLAYER IS BUSY\r\n"
game_starting = "200 YALP\nYou have entered into a game with "
game_starting_o = "200 OYALP\nYou have entered into a game with "
icon_assignment = "Your icon will be "
o_icon = "O and you will move second."
x_icon = "X and you will move first."
invalid_move = "400 ERROR\nINVALID MOVE\r\n"
wrong_turn = "400 ERROR\nNOT YOUR TURN\r\n"
good_move = "200 ECALP\n"
good_opponent_move = "200 OECALP\n"
x = 'X'
o = 'O'
you_won = "200 WON\nYou win.\r\n"
you_tie = "200 TIE\nYou tied.\r\n"
opp_tie = "200 OTIE\nYou tied\r\n"
you_lost = "200 LOSE\n"
dot = '.'
exit_success = '200 TIXE\nSuccesful exit\r\n'
opponent_exited = '200 OTIXE\nYour opponenet just exited.\r\n'

# PROTOCOL CONSTANTS

class ThreadedTCPCommunicationHandler(BaseRequestHandler):
    def handle(self):
        #all the game state global variables
        global player_list
        global games_list
        global game_counter
        global auto_player_queue
        #booleans to designate game state
        player_name = ""
        logged_in = False
        in_lobby = False
        in_game = False

        auto_logged = False
        # a while loop in which all communication with socket is processed
        while 1:
            # This is where auto-login searches for a partner for you
            if auto_logged and search_for_player_name(player_name).aval is True:

                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if "EXIT" in string_message:

                    self.request.sendall(exit_success.encode())
                    auto_player_queue.remove(search_for_player_name(player_name))
                    player_list.remove(search_for_player_name(player_name))
                    break
                else:
                    pass


            # LOGIN STATE
            if not logged_in:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if 'AUTOLOGIN' in string_message:
                    return_str = string_message.split("AUTOLOGIN ")[1]
                    if '\r\n' in return_str:
                        username = return_str.split("\r\n")[0]
                        if auto_login(username, self.request):
                            self.request.sendall(success.encode())
                            player_name = username
                            logged_in = True
                            auto_logged = True
                            # let's connect top guy in the queue with you
                            if not not auto_player_queue:
                                player_2 = auto_player_queue[0]
                                if player_2 is search_for_player_name(player_name):
                                    if len(auto_player_queue) == 1:
                                        continue
                                    player_2 = auto_player_queue[1]
                                auto_player_queue.remove(player_2)
                                auto_player_queue.remove(search_for_player_name(player_name))
                            else:
                                continue
                            if player_2.aval is False:
                                continue
                            # start a game:
                            player_2.set_aval(False)
                            player_2.set_tic('O')
                            search_for_player_name(player_name).set_aval(False)
                            search_for_player_name(player_name).set_tic('X')
                            new_game = Game(game_counter, search_for_player_name(player_name), player_2)
                            games_list.append(new_game)
                            ret = ""
                            ret += game_starting + player_2.player_name + newline + icon_assignment + x_icon + carriage
                            self.request.sendall(ret.encode())
                            ret = ""
                            ret += game_starting_o + player_name + newline + icon_assignment + o_icon + carriage
                            player_2.fd.sendall(ret.encode())
                            game_counter += 1
                            player_2.current_game = new_game
                            search_for_player_name(player_name).current_game = new_game
                            search_for_player_name(player_name).turn = True
                            player_2.turn = False
                        else:
                            self.request.sendall(name_taken.encode())
                    else:
                        self.request.sendall(bad_format.encode())

                elif 'LOGIN ' in string_message:
                    #login player
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
            #IN LOBBY
            elif in_lobby and search_for_player_name(player_name).aval:
                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                if not search_for_player_name(player_name).aval:
                    continue
                #Who command
                if "WHO" in string_message:
                    return_str = string_message.split("WHO")[1]
                    if '\r\n' in return_str:
                        ret = ""
                        ret += who_success
                        for player in player_list:
                            if player.player_name != player_name and player.aval is True and not player.auto:
                                ret += player.player_name
                                ret += comma
                        ret += carriage
                        self.request.sendall(ret.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                #PLAY command
                elif "PLAY " in string_message:
                    return_str = string_message.split("PLAY ")[1]
                    if '\r\n' in return_str:
                        username = return_str.split("\r\n")[0]
                        if search_for_player_name(username) is not None:
                            player = search_for_player_name(username)
                            if player.aval and not player.auto and player is not search_for_player_name(player_name):
                                new_game = Game(game_counter, search_for_player_name(player_name), player)
                                games_list.append(new_game)
                                search_for_player_name(player_name).set_aval(False)
                                search_for_player_name(player_name).set_tic('X')
                                ret = ""
                                ret += game_starting + username + newline + icon_assignment + x_icon + carriage
                                self.request.sendall(ret.encode())
                                ret = ""
                                player.set_aval(False)
                                player.set_tic('O')
                                ret += game_starting_o + player_name + newline + icon_assignment + o_icon + carriage
                                player.fd.sendall(ret.encode())
                                game_counter += 1
                                player.current_game = new_game
                                search_for_player_name(player_name).current_game = new_game
                                search_for_player_name(player_name).turn = True
                                player.turn = False

                            else:
                                self.request.sendall(busy_player_name.encode())
                        else:
                            self.request.sendall(invalid_player_name.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                #GAMES command
                elif "GAMES" in string_message:
                    return_str = string_message.split("GAMES")[1]
                    if '\r\n' in return_str:
                        ret = ""
                        ret += games_success
                        for game in games_list:

                            ret += player_one_intro + game.player_x.player_name + player_two_intro + game.player_o.player_name + comma
                        ret += carriage
                        self.request.sendall(ret.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                #exit command
                elif "EXIT" in string_message:
                    return_str = string_message.split("EXIT")[1]
                    if '\r\n' in return_str:
                        self.request.sendall(exit_success.encode())
                        player_list.remove(search_for_player_name(player_name))
                        break
                    else:
                        self.request.sendall(bad_format.encode())
                else:
                    self.request.sendall(bad_format.encode())
            #GAME STATE
            elif search_for_player_name(player_name) is not None and search_for_player_name(
                        player_name).aval is False:


                self.data = self.request.recv(1024)
                string_message = self.data.decode("utf-8")
                #PLACE command while in game
                if "PLACE " in string_message:
                    return_str = string_message.split("PLACE")[1]
                    if not search_for_player_name(player_name).turn:
                        self.request.sendall(wrong_turn.encode())
                    elif "\r\n" in return_str:
                        n = return_str.split("\r\n")[0]
                        if move_on_board(search_for_player_name(player_name).current_game.board_array, int(n), search_for_player_name(player_name).tic):
                            ret = ""
                            ret += good_move
                            for row in search_for_player_name(player_name).current_game.board_array:
                                for item in row:
                                    ret += item
                                ret += comma
                            ret += carriage
                            self.request.sendall(ret.encode())
                            ret = ""
                            if search_for_player_name(player_name).current_game.turn is search_for_player_name(player_name).current_game.player_x:
                                ret += good_opponent_move
                                for row in search_for_player_name(player_name).current_game.board_array:
                                    for item in row:
                                        ret += item
                                    ret += comma
                                ret += carriage
                                search_for_player_name(player_name).current_game.player_o.fd.sendall(ret.encode())
                                search_for_player_name(player_name).current_game.turn = search_for_player_name(player_name).current_game.player_o
                                search_for_player_name(player_name).current_game.player_o.turn = True
                                search_for_player_name(player_name).current_game.player_x.turn = False
                            else:
                                ret += good_opponent_move
                                for row in search_for_player_name(player_name).current_game.board_array:
                                    for item in row:
                                        ret += item
                                    ret += comma
                                ret += carriage
                                search_for_player_name(player_name).current_game.player_x.fd.sendall(ret.encode())
                                search_for_player_name(player_name).current_game.turn = search_for_player_name(player_name).current_game.player_x
                                search_for_player_name(player_name).current_game.player_x.turn = True
                                search_for_player_name(player_name).current_game.player_o.turn = False
                            # check win conditions and end game if necessary

                            if check_win_conditions(search_for_player_name(player_name).current_game.board_array) == 1:
                                search_for_player_name(player_name).current_game.player_x.fd.sendall(you_won.encode())
                                search_for_player_name(player_name).current_game.player_x.aval = True
                                search_for_player_name(player_name).current_game.player_o.fd.sendall(you_lost.encode())
                                search_for_player_name(player_name).current_game.player_o.aval = True
                                games_list.remove(search_for_player_name(player_name).current_game)

                            elif check_win_conditions(search_for_player_name(player_name).current_game.board_array) == 2:
                                search_for_player_name(player_name).current_game.player_o.fd.sendall(you_won.encode())
                                search_for_player_name(player_name).current_game.player_x.aval = True
                                search_for_player_name(player_name).current_game.player_x.fd.sendall(you_lost.encode())
                                search_for_player_name(player_name).current_game.player_o.aval = True
                                games_list.remove(search_for_player_name(player_name).current_game)
                            tie = True
                            #Checks tie and ends game if necessary
                            for row in search_for_player_name(player_name).current_game.board_array:
                                for item in row:
                                    if item == '.':
                                        tie = False
                            if tie:
                                self.request.sendall(you_tie.encode())
                                search_for_player_name(player_name).current_game.player_x.aval = True
                                search_for_player_name(player_name).current_game.player_o.aval = True
                                if search_for_player_name(player_name).current_game.player_x is search_for_player_name(player_name):
                                    search_for_player_name(player_name).current_game.player_o.fd.sendall(opp_tie.encode())
                                else:
                                    search_for_player_name(player_name).current_game.player_x.fd.sendall(opp_tie.encode())
                                games_list.remove(search_for_player_name(player_name).current_game)
                            if check_win_conditions(search_for_player_name(player_name).current_game.board_array) > 0 or tie:
                                #if player was autologged, makes new game
                                if auto_logged:
                                    auto_player_queue.append(search_for_player_name(player_name).current_game.player_o)
                                    auto_player_queue.append(search_for_player_name(player_name).current_game.player_x)
                                    search_for_player_name(player_name).current_game.player_x.aval = True
                                    search_for_player_name(player_name).current_game.player_o.aval = True

                                    if not not auto_player_queue:
                                        player_2 = auto_player_queue[0]
                                        if player_2 is search_for_player_name(player_name):
                                            if len(auto_player_queue) == 1:
                                                continue
                                            player_2 = auto_player_queue[1]
                                        auto_player_queue.remove(player_2)
                                        auto_player_queue.remove(search_for_player_name(player_name))
                                    else:
                                        continue

                                    # start a game:
                                    player_2.set_aval(False)
                                    player_2.set_tic('O')
                                    search_for_player_name(player_name).set_aval(False)
                                    search_for_player_name(player_name).set_tic('X')
                                    new_game = Game(game_counter, search_for_player_name(player_name), player_2)
                                    games_list.append(new_game)
                                    ret = ""
                                    ret += game_starting + player_2.player_name + newline + icon_assignment + x_icon + carriage
                                    self.request.sendall(ret.encode())
                                    ret = ""
                                    ret += game_starting_o + player_name + newline + icon_assignment + o_icon + carriage
                                    player_2.fd.sendall(ret.encode())
                                    game_counter += 1
                                    player_2.current_game = new_game
                                    search_for_player_name(player_name).current_game = new_game
                                    search_for_player_name(player_name).turn = True
                                    player_2.turn = False



                        else:
                            self.request.sendall(invalid_move.encode())
                    else:
                        self.request.sendall(bad_format.encode())
                #handles exit while in a game
                elif "EXIT" in string_message:
                    return_str = string_message.split("EXIT")[1]
                    if '\r\n' in return_str:

                        self.request.sendall(exit_success.encode())
                        if search_for_player_name(player_name) is search_for_player_name(player_name).current_game.player_x:
                            search_for_player_name(player_name).current_game.player_o.fd.sendall(opponent_exited.encode())
                            search_for_player_name(player_name).current_game.player_o.aval = True
                            if auto_logged:
                                auto_player_queue.append(search_for_player_name(player_name).current_game.player_o)

                        else:
                            search_for_player_name(player_name).current_game.player_x.fd.sendall(opponent_exited.encode())
                            search_for_player_name(player_name).current_game.player_x.aval = True
                            if auto_logged:
                                auto_player_queue.append(search_for_player_name(player_name).current_game.player_x)
                        games_list.remove(search_for_player_name(player_name).current_game)
                        player_list.remove(search_for_player_name(player_name))


                        break
                    else:
                        self.request.sendall(bad_format.encode())
                else:
                    self.request.sendall(bad_format.encode())


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 1234
    server = ThreadedTCPServer(('', PORT), ThreadedTCPCommunicationHandler)
    server.serve_forever()
