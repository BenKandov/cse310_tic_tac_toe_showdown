from sys import argv, stdin
from socket import *
import select

# boolean for exiting; start as True
running = True

def help_cmd(exec_args):
    print('This is the help menu')

def login(exec_args):
    if len(exec_args['c_args']) < 1:
        print('You must choose a name to login as')
    elif len(exec_args['c_args'][0]) > 50:
        print('Your username can only be 50 characters at most')
    else:
        username = exec_args['c_args'][0]
        protocol_cmd = 'LOGIN %s\r\n' % (username,)
        exec_args['socket'].send(protocol_cmd.encode())

def place(exec_args):
    if len(exec_args['c_args']) < 1:
        print('Please specify which cell you like to make your move in')
    else:
        cell = exec_args['c_args'][0]
        protocol_cmd = 'PLACE %s\r\n' % (cell,)
        exec_args['socket'].send(protocol_cmd.encode())

def exit_game(exec_args):
    global running

    protocol_cmd = 'EXIT\r\n'
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
        exec_args['socket'].send(protocol_cmd.encode())

def handle_msg(msg):
    # msg is an array of string
    print('this is what is sent: ' + msg[0])
    if msg[0] == '200 OHW\n':
        print('These players are on right now:')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    elif msg[0] == '200 SEMAG\n':
        print('These are the current games:')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    elif msg[0] == '200 ECALP\n':
        print('You played a move: ')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    elif msg[0] == "200 OECALP\n":
        print('The opponent has made his/her move: ')
        to_print = msg[1].split(',')
        for x in to_print:
            print(x)
    else:
        print(msg[1])

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
            # if the being run with the automatch flag, then send a quick AUTOMATCH req
            client_soc.send('AUTOLOGIN\r\n'.encode())
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
                    handle_msg(message)
