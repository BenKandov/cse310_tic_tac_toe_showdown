from sys import argv
from socket import *

# command line args
hostname = argv[1]
port = int(argv[2])

# boolean for exiting; starts as True
running = True

def help_cmd(exec_args):
    print('This is the help menu')

def login(exec_args):
    if not exec_args['c_args']:
        print('You must choose a name to login as')
    else:
        username = exec_args['c_args'][0]
        exec_args['socket'].send(username.encode())
        ack = exec_args['socket'].recv()
        ack = ack.decode()
        
        if ack == 'y':
            # if server responds with 'y', it worked
            print('Your username is now %s' % (username,))
        elif ack == 't':
            # if server responsds with 't', that username is taken already
            print('That username is already taken')
        else:
            # the protocol is not being followed if you end up here
            print('Could not decode server response')

def place(exec_args):
    if not exec_args['c_args']:
        print('Which cell you like to make your move in?')
    else:
        cell = exec_args['c_args']
        exec_args['socket'].send(str(cell).encode()) # sending cell as a string
        ack = exec_args['socket'].recv()
        ack = ack.decode()

        if ack == 'n':
            # server sent back an error, illegal move
            print('Illegal move')
        else:
            # server sent back a board you can print
            print(ack)

def exit_game(exec_args):
    global running

    running = False
    exec_args['socket'].close()
    print('Thanks for playing')

# dictionary of function pointers to make cmd parsing easy
commands = {
        'help': help_cmd,
        'login': login,
        'place': place,
        'exit': exit_game
}

if __name__ == '__main__':
    if not argv[1] and not arg[2]:
        print('This program needs a hostname and port')
    else: 
        client_soc = socket.socket(AF_INET, SOCK_STREAM)
        client_soc.connect( (hostname, port) )
        
        while running:
            cmd = input('Type a command (or help if you are not sure): ')
            sanitized = cmd.strip() # strip beginning & ending whitespace
            parse_list = sanitized.split(' ', 1) # split into func name and rest of args

            exec_func = parse_list[0] # take out the actual function call
            exec_args = { 'socket': client_soc} # always gets passed to the command functions

            if len(parse_list) > 1:
                # if a command takes args, then the functions now have access to them
                exec_args['c_args'] = list(filter(lambda x: x != '', parse_list[1].split(' '))) 

            if exec_func not in commands:
                print('Not a valid command')
            else:
                commands[exec_func](exec_args)
