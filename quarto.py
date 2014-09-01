import numpy as np
import cmd
import re


# check if a given 4 locations have a winning combination
# max!=16 checks that there are no empy spaces
# bitwise_and looks for any characteristic that is all 1s
# bitwise_or is less than 15 only if there is a position which has no 1 (all 0)
# in any of the 4 items in the row
# between these two conditions I check for either all 1 or 0 in a position
def check_row(row):
    # print row
    res = bool((row.max() != 16) and (reduce(np.bitwise_and, row) or (reduce(np.bitwise_or, row) < 15)))
    # print (row.max() != 16)
    # print reduce(np.bitwise_and, row)
    # print (reduce(np.bitwise_or, row) < 15)
    # print (reduce(np.bitwise_and, row) or (reduce(np.bitwise_or, row) < 15))
    # print 'res', res
    return res

def check_win(board):
    # check each row and column for a winning group
    for i in xrange(4):
        if check_row(board[i]) or check_row(board[:,i]):
            return True
    # check diagonals, returning True is either is winning, else False
    return check_row(np.diag(board)) or check_row(np.diag(np.fliplr(board)))

# function to map string for piece to number, assumer proper formatting (lower, 4 char, etc)
def piece_to_num(key):
    num = ''
    if key[0] == 't':
        num += '0'
    else:
        num += '1'
    if key[1] == 'r':
        num += '0'
    else:
        num += '1'
    if key[2] == 's':
        num += '0'
    else:
        num += '1'
    if key[3] == 's':
        num += '0'
    else:
        num += '1'
    return int(num, 2)
# SHOULD JUST HAVE A DICT!!!!
def num_to_piece(num):
    if num == 16:
        return '    '
    piece = ''
    if num >> 3 & 1:
        piece += 's'
    else:
        piece += 't'
    if num >> 2 & 1:
        piece += 'b'
    else:
        piece += 'r'
    if num >> 1 & 1:
        piece += 'c'
    else:
        piece += 's'
    if num & 1:
        piece += 'h'
    else:
        piece += 's'
    return piece

def display_board(board):
    def printable_row(row):
        return '| ' + ' | '.join(map(num_to_piece,row)) + ' |'
    hr = '  ' + '-' * 29 + '\n'
    # empty row
    spacer = '  ' + printable_row([16,16,16,16])
    print '     ' + '      '.join(map(str,range(4)))
    for i in range(4):
        print hr + spacer + '\n' + str(i) + ' ' + printable_row(board[i]) + '\n' + spacer
    print hr

t = np.arange(16).reshape([4,4])

def available_pieces(pieces):
    return pieces

def check_piece_pickable(piece, pieces):
    return (piece in pieces)

# assume already checked that the piece is available to place
def place_piece(row, col, piece, board):
    # place must be open
    if board[row,col] != 16:
        return False
    # place piece
    else:
        board[row,col] = piece
        return True

# check if winning board
# ?????




class Quarto(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)

        # create board, a 4x4 grid filled with 16
        # 16 is defined as an empty space
        self.board = np.empty([4,4], dtype=int)
        self.board.fill(16)

        # create piece set
        # each of the 16 pieces can be uniquely and canonically described
        # by the 4 bit 0-15, each bit represents 1 of the characteristics
        # Characteristics (0/1):
        # tall/short
        # red/blue
        # square/circle
        # solid/hollow
        # So, for example, piece 0 (0000) is tall red square solid.
        # and piece 7 (0111) is tall blue circle hollow
        self.pieces = set(range(16))

        self.current_player = 0

        self.prompt = 'Player 1: '

    def prompt_text(self, player):
        return 'Player ' + str(player) + ': '

    def do_EOF(self, line):
        print
        return True

    def do_exit(self, line):
        print
        return True

    def do_display_board(self, line):
        display_board(self.board)

    def do_show_pieces(self, line):
        for piece in self.pieces:
            print num_to_piece(piece)

    def do_status(self):
        print 'It is currently Player ' + str(self.current_player) + "'s turn. \nPlayer " + str((self.current_player + 1) % 2) + " should choose a piece for Player " + str(self.current_player) + " to place."

    def get_placement(self, current_player, piece):
        print 'Player ' + str(current_player) + ' places ' + num_to_piece(piece) + '. Enter RowNumber and ColumnNumber as a two digit number (i.e. 12 for row 1 column 2).'
        display_board(self.board)
        placement = raw_input(self.prompt_text(current_player))
        while not re.search('[0-3][0-3]', placement):
            print 'Invalid placement command. \nEnter RowNumber and ColumnNumber as a two digit number (i.e. 12 for row 1 column 2) to place ' + num_to_piece(piece) + '.'
            display_board(self.board)
            placement = raw_input(self. prompt_text(current_player))

        row = int(placement[0])
        col = int(placement[1])

        return row, col


    def do_pick(self, line):
        
        # check if piece is valid and then convert to number 
        if not re.search('[ts][rb][sc][sh]',line):
            print 'That is not a valid piece. Please try again.'
            return False
        else:
            piece = piece_to_num(line)

        if check_piece_pickable(piece, self.pieces):
            # remove piece from the set of available pieces
            self.pieces.remove(piece)

            row, col = self.get_placement(self.current_player, piece)

            while not place_piece(row, col, piece, self.board):
                print 'This place is already occupied by a piece'
                row, col = self.get_placement(self.current_player, piece)

            # check winning
            if check_win(self.board):
                print 'Congratulations Player ' + str(self.current_player) + "! You've Won!"
                display_board(self.board)
                print
                return True

            else:
                self.current_player = (self.current_player + 1) % 2
                self.prompt = self.prompt_text(self.current_player)
                print 'It is currently Player ' + str(self.current_player) + "'s turn. \nPlayer " + str((self.current_player + 1) % 2) + " should choose a piece for Player " + str(self.current_player) + " to place."
                return False

        else:
            print 'That piece has already been played. \nEnter show_pieces to see available pieces.'





