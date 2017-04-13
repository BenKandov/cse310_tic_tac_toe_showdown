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

    # check for diagonal wins

    # check for row wins
    for row in board_array:
        if (board_array[row][0] == board_array[row][1]) and \
                (board_array[row][1] == board_array[row][2]):
            if board_array[row][0].contains('X'):
                return 2
            else:
                return 1
    # check for column wins

    return 0


move_on_board(3, 'X ')
move_on_board(5, 'O ')
print_board()
