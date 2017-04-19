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
