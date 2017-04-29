from sys import argv

# command line args
#hostname = argv[1]
#port = int(argv[2])

# boolean for exiting; starts as True
running = True

def help_cmd(exec_args):
    print('This is the help menu')

def login(exec_args):
    pass

def place(exec_args):
    print(exec_args['socket'])
    print(exec_args['cmd_args'])

def exit_game(exec_args):
    global running
    running = False
    print('Thanks for playing')

commands = {
        'help': help_cmd,
        'login': login,
        'place': place,
        'exit': exit_game
}

if __name__ == '__main__':
    while running:
        cmd = input('Type a command (or help if you are not sure): ')
        sanitized = cmd.strip() # strip beginning & ending whitespace
        parse_list = sanitized.split(' ', 1)

        exec_func = parse_list[0] # take out the actual function call
        exec_args = { 'socket': 3} # always gets passed to the command functions

        if len(parse_list) > 1:
            # if a command takes args, then the functions now have access to them
            exec_args['cmd_args'] = list(filter(lambda x: x != '', parse_list[1].split(' '))) 
        if exec_func not in commands:
            print('Not a valid command')
        else:
            commands[exec_func](exec_args)
