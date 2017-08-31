from typing import Tuple, List
import curses

BoardPos = Tuple[int, int]
BoardState = {'No Win', '1 Win', '2 Win'}

class board(object):

    # NOTE: Left Edge is player 1, and
    # I have NOT tested with non-square boards
    def __init__(self, size:BoardPos=(11,11)):
        assert(len(size) == 2)
        assert(size[0] > 1 and size[1] > 1)

        self.board = [[0] * size[0] for _ in range(size[1])]
        self.size = size
        self.debug = 'NONE'

    # Return if a move is legal or not
    def legal(self, pos:BoardPos) -> bool:
        try:
            return self.board[pos[1]][pos[0]] == 0
        except:
            return False

    def listlegals(self) -> List[BoardPos]:
        ret = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self.legal((x, y)):
                    ret += [(x, y)]
        return ret


    # Return a list of touching positions
    def adjacent(self, pos:BoardPos) -> List[BoardPos]:
        # Find if the piece is on any edge(s)
        leftedge, rightedge = pos[0] == 0, pos[0] == self.size[0] - 1
        topedge, bottomedge = pos[1] == 0, pos[1] == self.size[1] - 1
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
        # Check for Player 1 Victory
        leftside = [self.board[i][0] for i in range(self.size[0])]
        currents = []
        visited = []
        for y, l in enumerate(leftside):
            if l is 1:
                currents += [(0,y)]
        while len(currents) > 0:
            cbuffer = []
            for c in currents:
                if c[0] == self.size[0] - 1:
                    # Player 1 has won
                    return '1 Win'
                for adj in self.adjacent(c):
                    if not adj in visited and self.board[adj[1]][adj[0]] == 1:
                        cbuffer += [adj]
                        visited += [adj]
            currents = cbuffer

        # Check for Player 2 Victory
        topside = self.board[0]
        currents = []
        visited = []
        for x, l in enumerate(topside):
            if l is 2:
                currents += [(x, 0)]
        while len(currents) > 0:
            cbuffer = []
            for c in currents:
                if c[1] == self.size[1] - 1:
                    # Player 2 has won
                    return '2 Win'
                for adj in self.adjacent(c):
                    if not adj in visited and self.board[adj[1]][adj[0]] == 2:
                        cbuffer += [adj]
                        visited += [adj]
            currents = cbuffer

        return 'No Win'


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

def cGame(stdscr = None, p1ai = None, p2ai = None):
    # Initialize Curses
    if stdscr is None:
        stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    curses.start_color()

    # Setup the color pairs
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

    selectedpos = (0, 0)
    b = board()
    psturn = 1

    def drawface(stdscr, selectedpos, b, psturn):

        stdscr.erase()
        stdscr.border()
        stdscr.addstr(0, 10, "HEX ('q'=quit,Space=move)")
        stdscr.addstr(0, 40, "P" + str(psturn) + ' turn', curses.color_pair(psturn))
        # Draw the winner
        stdscr.addstr(17, 10, "Status: " + b.boardstate())

        # TEMPORARY: Add a debug message
        # from AI import hyperScoreAI
        # a = hyperScoreAI(player=1)
        # b.debug = str(a.lightDistance(b))

        # Draw the debug info
        # stdscr.addstr(18, 10, "Debug :" + b.debug)
        # stdscr.addstr(19, 10, "Pos :" + str(selectedpos))

        scrnpos = [4,5]
        count = 0

        # Add the top row of -'s for 2
        stdscr.addstr(scrnpos[0]-1, scrnpos[1]+1, '-'*(b.size[0]*2-1), curses.color_pair(2))

        for y, row in enumerate(b.board):
            count += 1

            # Add the left row of \'s for 1
            stdscr.addstr(scrnpos[0], scrnpos[1] + count - 1, '\\', curses.color_pair(1))

            for x, itm in enumerate(row):

                if itm in [1, 2]:
                    stdscr.addstr(scrnpos[0], scrnpos[1] + count, str(itm),
                                  curses.color_pair(itm))
                    if (x,y) == selectedpos:
                        stdscr.addstr(scrnpos[0], scrnpos[1] + count - 1, '>',
                                      curses.color_pair(itm))
                        stdscr.addstr(scrnpos[0], scrnpos[1] + count + 1, '<',
                                      curses.color_pair(itm))
                else:
                    stdscr.addstr(scrnpos[0], scrnpos[1] + count, str(itm) if itm is not 0 else '*',
                                  curses.A_REVERSE if selectedpos == (x, y) else curses.A_NORMAL)

                scrnpos[1] += 2

            # Add the right row of \'s for 1
            stdscr.addstr(scrnpos[0], scrnpos[1] + count - 1, '\\', curses.color_pair(1))

            scrnpos[1] = 5
            scrnpos[0] += 1
        # Add the bottom row of -'s for 2
        stdscr.addstr(scrnpos[0], scrnpos[1] + (b.size[0] * 2 - 11), '-' * (b.size[0] * 2 - 1), curses.color_pair(2))

        stdscr.refresh()

    # Enter main loop
    drawface(stdscr, selectedpos, b, psturn)
    while True:
        # Let the AI move if it exists
        if psturn is 1 and p1ai is not None:
            b.move(p1ai(b), 1)
            psturn = 2
            drawface(stdscr, selectedpos, b, psturn)
            continue
        if psturn is 2 and p2ai is not None:
            b.move(p2ai(b), 2)
            psturn = 1
            drawface(stdscr, selectedpos, b, psturn)
            continue

        c = stdscr.getch()
        if c == ord('q'):
            break # Quit from game
        elif c == ord('a'):
            selectedpos = ((selectedpos[0] - 1) % 11, (selectedpos[1]) % 11)
            drawface(stdscr, selectedpos, b, psturn)
        elif c == ord('d'):
            selectedpos = ((selectedpos[0] + 1) % 11, (selectedpos[1]) % 11)
            drawface(stdscr, selectedpos, b, psturn)
        elif c == ord('s'):
            selectedpos = ((selectedpos[0]) % 11, (selectedpos[1] + 1) % 11)
            drawface(stdscr, selectedpos, b, psturn)
        elif c == ord('w'):
            selectedpos = ((selectedpos[0]) % 11, (selectedpos[1] - 1) % 11)
            drawface(stdscr, selectedpos, b, psturn)
        elif c == ord(' '):
            if b.legal(selectedpos):
                b.move(selectedpos, psturn)
                psturn = 1 if psturn is 2 else 2
                drawface(stdscr, selectedpos, b, psturn)



    # Clean up the console
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

if __name__ == '__main__':
    from sys import argv
    from AI import doubleProbDropAI, hyperScoreAI
    try:
        argv[1]
    except:
        print('Please provide which CPU (if any) to play against as an argument!!!')
        exit(1)
    t = argv[1]
    if t == 'local':
        cGame()
    elif t == 'hscore':
        ai = hyperScoreAI(2)
        cGame(p2ai=ai)
    elif t == 'dprop':
        ai = doubleProbDropAI(2)
        cGame(p2ai=ai)