import numpy as np

class Minefield:
    '''The logic for setting up and playing a game of minesweeper.

    Class Attributes:
        __diff_mode (dict): A tuple with the mine_amount, width, and height for each respective difficulty level.
        _game_lost (bool): Flag for whether the game is lost, which occurs when a mine is dug up. Set as False.
    
    Instance Attributes:
        width (int): The number of columns in the minefield.
        height (int): The number of rows in the minefield.
        mine_amnt (int): Total nusmber of mines.
        field (2D Array): The minefield layout where each element is either a mine represented by -1, or a natural number of mines the element touches.
        field_map (2D Array): The status of the minefield locations, whether the elements are buried (0), dug (1), or flagged (2).
    '''
    __diff_mode = {'EASY' : (10,8,8), 'MED' : (40,15,15), 'HARD' : (40,30,16)}
    _game_lost = False

    def __init__(self, mode):
        '''Creates an instance of a Minefield with dimensions and mine amount determined by the difficulty level passed.

        Arguments:
            mode (str): One of the following difficulty leveles - 'EASY', 'MED', 'HARD'.
        '''
        self.mine_amnt, self.width, self.height = Minefield.__diff_mode[mode]
        self.__create_field()
        self.__locate_mines()
        self.field_map = np.zeros((self.height, self.width))

    def __create_field(self):
        '''Creates the field with a zero array of size height by width with the mine amount of negative ones randomly shuffled throughout.'''
        self.field = np.zeros((self.height * self.width), dtype = int)
        self.field[:self.mine_amnt] = np.full((self.mine_amnt), -1)
        np.random.shuffle(self.field)
        self.field = np.reshape(self.field, (self.height, self.width))

    def __locate_mines(self):
        '''Locates the indicies of the mines, and adds the number of mines each non-mine location touches (includes horizontal, vertical and diagonals).'''
        mine_locs = np.column_stack((np.nonzero(self.field)))
        for m_row, m_col in mine_locs:
            sur_locs = self.__surrounds(m_row, m_col)
            for row, col in sur_locs:
                if self.field[row, col] != -1:
                    self.field[row, col] += 1
    
    def __surrounds(self, loc_row, loc_col):
        '''Finds indices of all surrounding elements of the index location passed.
        
        Arguments:
            loc_row (int): The row index of the element to find surrounding elements.
            loc_col (int): The column index of the element to find surrounding elements.

        Return:
            valid_locs (2D Array): The indices of the surrounding elements that are within bounds.
        '''
        sur_row = [loc_row - 1] * 3 + [loc_row] * 2 + [loc_row + 1] * 3
        sur_col = [loc_col - 1, loc_col, loc_col + 1] * 3
        sur_col[4:5] = []
        sur_locs = np.transpose(np.array((sur_row, sur_col)))
        valid_locs = []
        for row, col in sur_locs:
            if 0 <= row < self.height and 0 <= col < self.width:
                valid_locs += [[row, col]]
        return np.array(valid_locs)
    
    def dig(self, loc_row, loc_col):
        '''Updates the field map to dug at the location index passed. For zero values, surrounding locations are dug until a natural number is reached.
        
        Arguments:
            loc_row (int): The row index of the element on the field map to be dug.
            loc_col (int): The column index of the element on the field map to be dug.
        '''
        if self.field_map[loc_row, loc_col] == 0:
            self.field_map[loc_row, loc_col] = 1
            if self.field[loc_row, loc_col] == -1:
                self._game_lost = True
            else:
                if self.field[loc_row, loc_col] == 0:
                    sur_locs = self.__surrounds(loc_row, loc_col)
                    for row, col in sur_locs:
                        self.dig(row, col)

    def flag(self, loc_row, loc_col):
        '''Updates the field map to the opposing flag status at the location index passed. Buried becomes flagged, and flagged becomes buried.
        
        Arguments:
            loc_row (int): The row index of the element on the field map whose flag status is to be changed.
            loc_col (int): The column index of the element on the field map whose flag status is to be changed.
        '''
        if self.field_map[loc_row, loc_col] == 0:
            self.field_map[loc_row, loc_col] = 2
        elif self.field_map[loc_row, loc_col] == 2:
            self.field_map[loc_row, loc_col] = 0
    
    def __str__(self):
        '''Prints the minefield.'''
        string = ''
        col_str = ' ' * 7 + ' '.join([f'{str(i) : <2}' for i in range(1, self.width + 1)])
        barrier = ' ' * 3 + "=" * (self.width * 3 + 6)
        string += (f'{col_str}\n'  + f'{barrier}\n')
        for row in range(self.height):
            row_str = f'{row + 1 : <2} || '
            for col in range(self.width):
                if self.field_map[row, col] == 0:
                    row_str += ' - '
                elif self.field_map[row, col] == 2:
                    row_str += ' F '
                elif self.field_map[row, col] == 1:
                    s = self.field[row, col]
                    if s == -1:
                        row_str += f' M '
                    else:
                        row_str += f' {s} '
            string += (row_str + f' || {row + 1}\n')
        string += (f'{barrier}\n' + f'{col_str}\n')
        return string

    @property
    def game_won(self):
        '''Determines whether all non-mine locations are dug up. Returns True if all non-mine locations are dug up, otherwise False.'''
        self._game_won = False
        if not self.game_lost:
            if np.count_nonzero(self.field_map == 1) == self.height * self.width - self.mine_amnt:
                self._game_won = True
        return self._game_won
    
    @property
    def game_lost(self):
        '''Returns True if a mine was dug up, otherwise False.'''
        return self._game_lost
    
    @staticmethod
    def play():
        '''Play a version of the game of Minesweeper that can be played in the terminal.'''
        htp = '''
The goal of the game is to find where all mines in a minefield are located without accidentally triggering a landmine!
There are two actions that you can complete to acheive this goal.
Dig: Reveals the status of an undug location (represented by '-').
\t If a mine (represented by 'M') is revealed, you lose.
\t If a number is revealed, that is the amount of mines in the location's immediate surroundings (diagonals included).
\t If a zero is revealed, the location's surroundings will be automatically dug up for you as there are no mines.
Flag: Updates the mine status of an undug location.
\t If there is an undug location, the location becomes flagged (represented by 'F').
\t If there is a flagged location, the location returns to an undug status.
\t Locations that are flagged represent that a mine is present and cannot be dug up.
To complete an action at a specific location:
\t Type the first letter of the respective action followed by the desired location.
\t For example, to dig at the location 5 rows down 6 columns over, type 'D 5 6'.
To win the game, all non-mine locations must be dug up! (Mines can either be flagged of left undug)\n'''

        print('Welcome to Minesweeper - Olivia\'s Version!')
        htp_input = True
        while htp_input:
            h = input('Would you like to see how to play? (Y/N): ')
            htp_input = False
            if h.upper() == 'Y':
                print(htp)
            elif h.upper() != 'N':
                print('I am sorry, input not recognized!')
                htp_input = True
        diff = None
        diff_input = True
        while diff_input:
            d = input('Please select one of the following gamemodes - Easy (E), Medium (M), Hard (H): ')
            diff_input = False
            if d.upper() == 'E':
                diff = 'EASY'
            elif d.upper() == 'M':
                diff = 'MED'
            elif d.upper() == 'H':
                diff = 'HARD'
            else:
                print('I am sorry, input not recognized!')
                diff_input = True
        game = Minefield(diff)
        while True:
            print(game)
            i = input('Please input next move: ')
            try:
                action, y_coord, x_coord = i.split(' ')
            except ValueError:
                print('Coordinate seems incorrect. Try again!')
                continue
            action, y_coord, x_coord = i.split(' ')
            action = action.upper()
            y_coord = int(y_coord) - 1
            x_coord = int(x_coord) - 1
            if action != 'D' and action != 'F':
                print('Action not recognized. Try again!')
                continue
            elif not (0 <= y_coord < game.height):
                print('Row location is out of bounds. Try again!')
                continue
            elif not (0 <= x_coord < game.width):
                print('Column location is out of bounds. Try again!')
                continue
            if action == 'D':
                game.dig(y_coord, x_coord)
                if game.game_lost:
                    print(game)
                    print('BOOOOOOM!!!!! Oh no! You hit a mine and have lost!')
                    break
                elif game.game_won:
                    print(game)
                    print('CONGRADULATIONS!!!!! You have successfully navigated the minefield!')
                    break
            elif action == 'F':
                game.flag(y_coord, x_coord)
        if input('Would you like to play again? (Y/N): '):
            Minefield.play()
        else:
            print('Thanks for playing!')
                
Minefield.play()