from sys import argv, stdin
from socket import *
import select

# boolean for exiting; start as True
running = True

def help_cmd(exec_args):
    print('\n')
    print('These commands can be used at all times:')
    print('--------------------------------------------------')
    print('help - prints help menu')
    print('login [username] - logs in a person under the specified username')
    print('place [cell] - places your mark on the the tic-tac-toe board on the specified cell number')
    print('exit - exits the program')
    print('These commands can only be used when AUTOLOGIN is not specified:')
    print('--------------------------------------------------')
    print('games - prints all current games going on now')
    print('who - show which games are currently being played')
    print('play [username] - start a game with the player with the specified username')
    print('\n')

def login(exec_args):
    if len(exec_args['c_args']) < 1:
        print('You must choose a name to login as')
    elif len(exec_args['c_args'][0]) > 50:
        print('Your username can only be 50 characters at most')
    else:
        username = exec_args['c_args'][0]
        protocol_cmd = 'LOGIN %s\r\n' % (username,)
        #print('SENDING TO SERVER : %s', protocol_cmd)
        exec_args['socket'].send(protocol_cmd.encode())

def place(exec_args):
    if len(exec_args['c_args']) < 1:
        print('Please specify which cell you like to make your move in')
    else:
        cell = exec_args['c_args'][0]
        protocol_cmd = 'PLACE %s\r\n' % (cell,)
        #print('SENDING TO SERVER : %s', protocol_cmd)
        exec_args['socket'].send(protocol_cmd.encode())

def exit_game(exec_args):
    global running

    protocol_cmd = 'EXIT\r\n'
    #print('SENDING TO SERVER : %s', protocol_cmd)
    exec_args['socket'].send(protocol_cmd.encode())
    exec_args['socket'].close()
    running = False

def games(exec_args):
    protocol_cmd = 'GAMES\r\n'
    exec_args['socket'].send(protocol_cmd.encode())

def who(exec_args):
    protocol_cmd = 'WHO\r\n'
    exec_args['socket'].send(protocol_cmd.encode())

def play(exec_args):
    if len(exec_args['c_args']) < 1:
        print('Specify who you would like to play as')
    else:
        opponent = exec_args['c_args'][0]
        protocol_cmd = 'PLAY %s\r\n' % (opponent,)
        #print('SENDING TO SERVER : %s', protocol_cmd)
        exec_args['socket'].send(protocol_cmd.encode())

def handle_msg(msg, client_soc):
    # msg is an array of string
    if msg[0] == '200 OHW':
        print('These players are on right now:')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    elif msg[0] == '200 SEMAG':
        if msg[1].strip() == '':
            print('There are no games currently in progress')
        else: 
            print('These are the current games:')
            to_print = msg[1].split(',')
            for x in to_print:
                print(x)
    elif msg[0] == '200 ECALP':
        print('You played a move: ')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    elif msg[0] == "200 OECALP":
        print('The opponent has made his/her move: ')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
        # used for a certain condition
        if len(msg) > 3:
            # you got sent 200 WON
            client_soc.send('garbage\r\n'.encode())
            client_soc.recv(1024)
            print('Good job! You win!')
    elif msg[0] == "200 WON":
        # send ENTER
        client_soc.send('garbage\r\n'.encode())
        client_soc.recv(1024)
        print('Good job! You win!')
    elif  msg[0] == '200 OYALP':
        print(msg[1])
        print(msg[2])
        # send ENTER
        client_soc.send('ENTER'.encode())
    elif msg[0] == "200 YALP":
        print(msg[1])
        print(msg[2])
    elif msg[0] == "200 OTIXE":
        print(msg[1])
        # send ENTER
        client_soc.send('ENTER'.encode())
        client_soc.recv(1024)
    elif msg[0] == "200 OTIE":
        # send ENTER
        client_soc.send('ENTER'.encode())
        client_soc.recv(1024)
        print('The game ended in a tie\n')
    elif msg[0] == "200 LOSE":
        print('Sorry, but you lost this game :(')
    else:
        print(msg[1])

def autologin(exec_args):
    if len(exec_args['c_args']) < 1:
        print('You must choose a name to login as')
    elif len(exec_args['c_args'][0]) > 50:
        print('Your username can only be 50 characters at most')
    else:
        username = exec_args['c_args'][0]
        protocol_cmd = 'AUTOLOGIN %s\r\n' % (username,)
        #print('SENDING TO SERVER : %s', protocol_cmd)
        exec_args['socket'].send(protocol_cmd.encode())

commands = {
    'help': help_cmd,
    'login': login,
    'place': place,
    'exit': exit_game
}

if __name__ == '__main__':
    if len(argv) < 2:
        print('This program requires a hostname and port as an argument')
    elif len(argv) > 3 and argv[3] != 'a':
        print("You can use 'a' to specify the automatch flag")
    else:
        # command line args
        hostname = argv[1]
        port = int(argv[2])

        client_soc = socket(AF_INET, SOCK_STREAM)
        client_soc.connect( (hostname, port) )

        # this is what select chooses from
        read_list = [ stdin, client_soc ]

        if len(argv) > 3:
            # if being run with the automatch flag, then change the login command to autologin
            commands['login'] = autologin
        else:
            # client can make more advanced requests if not being automatched
            commands['games'] = games
            commands['play'] = play
            commands['who'] = who

        while running:
            print('Type a command (or help if you are not sure): ')
            # select will return 3 lists of active fds, you care about 'readable'
            readable, writeable, exceptional = select.select(read_list, [], [])           
            for r in readable:
                if r == stdin:
                    # the user typed a command, handle it
                    cmd = stdin.readline()
                    sanatized = cmd.rstrip('\n').strip() # strip the beginning & ending whitespace
                    parse_list = sanatized.split(' ', 1) # split into fun name and rest of args

                    exec_func = parse_list[0] # take out the actual function call
                    exec_args = { 'socket': client_soc } # always gets passed to the command functions

                    if len(parse_list) > 1:
                        # if a command takes args, then the functions now have access to them
                        exec_args['c_args'] = list(filter(lambda x: x != '', parse_list[1].split(' ')))

                    if exec_func not in commands:
                        print('Not a valid command')
                    else:
                        commands[exec_func](exec_args)
                else:
                    # you can read from the socket 
                    message = client_soc.recv(1024).decode()
                    message = message.split('\n')
                    handle_msg(message, client_soc)
