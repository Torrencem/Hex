from typing import Tuple, List
import curses

class board(object):

    BoardPos = Tuple[int,int]
    BoardState = {'No Win','1 Win','2 Win'}

    # NOTE: Left Edge is player 1,
    def __init__(self, size:BoardPos=(11,11)):
        assert(len(size) == 2)
        # The next assert is because otherwise it's a trivial game
        assert(size[0] > 1 and size[1] > 1)

        self.board = [[0] * size[0] for _ in range(size[1])]
        self.size = size

    # Return if a move is legal or not
    def legal(self, pos:BoardPos) -> bool:
        return self.board[pos[0]][pos[1]] == 0

    # Return a list of touching positions
    def adjacent(self, pos:BoardPos) -> List[BoardPos]:
        # Find if the piece is on any edge(s)
        leftedge, rightedge = pos[0] == 0, pos[0] == self.size[0]
        topedge, bottomedge = pos[1] == 0, pos[1] == self.size[1]
        # Make sure everything's sane
        assert(not (leftedge and rightedge))
        assert(not (topedge and bottomedge))

        # List to return
        ret = []

        # Probably the best way to do it
        if not leftedge:
            ret += [(pos[0]-1, pos[1])]
        if not rightedge:
            ret += [(pos[0]+1, pos[1])]
        if not topedge:
            ret += [(pos[0], pos[1]-1)]
        if not bottomedge:
            ret += [(pos[0], pos[1]+1)]

        # Now for everything weird
        if not bottomedge and not leftedge:
            ret += [(pos[0]-1, pos[1]+1)]
        if not topedge and not rightedge:
            ret += [(pos[0]+1, pos[1]-1)]

        return ret

    # Make a move
    def move(self, pos:BoardPos, color:{1, 2}):
        self.board[pos[1]][pos[0]] = color

    # Find out if either player has won yet
    def boardstate(self) -> BoardState:
        leftside = [self.board[i][0] for i in range(self.size[0])]
        print(leftside)

    def __str__(self):
        s = ''
        count = 0
        for row in self.board:
            for itm in row:
                s += (str(itm) + ' ') if itm is not 0 else '* '
            count += 1
            s += '\n' + (' '*count)
        return s

    def __repr__(self):
        return str(self)

# Initialize Curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(0)

selectedpos = (0, 0)
b = board()

def drawface():
    global stdscr, selectedpos, b
    stdscr.erase()
    stdscr.border()
    stdscr.addstr(0, 10, "HEX (Press 'q' to quit)")
    scrnpos = [2,3]
    count = 0
    for y, row in enumerate(b.board):
        count += 1
        for x, itm in enumerate(row):

            stdscr.addstr(scrnpos[0], scrnpos[1] + count, str(itm) if itm is not 0 else '*',
                          curses.A_REVERSE if selectedpos == (x,y) else curses.A_NORMAL)
            scrnpos[1] += 2
        scrnpos[1] = 3
        scrnpos[0] += 1
    stdscr.refresh()

# Enter main loop
drawface()
while True:
    c = stdscr.getch()
    if c == ord('q'):
        break # Quit from game

    elif c == ord('a'):
        selectedpos = ((selectedpos[0] - 1) % 11, (selectedpos[1]) % 11)
        drawface()
    elif c == ord('d'):
        selectedpos = ((selectedpos[0] + 1) % 11, (selectedpos[1]) % 11)
        drawface()
    elif c == ord('s'):
        selectedpos = ((selectedpos[0]) % 11, (selectedpos[1] + 1) % 11)
        drawface()
    elif c == ord('w'):
        selectedpos = ((selectedpos[0]) % 11, (selectedpos[1] - 1) % 11)
        drawface()




# Clean up the console
curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()