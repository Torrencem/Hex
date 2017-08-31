from random import choice
from math import sqrt
import numpy as np
from copy import deepcopy


# Compute the softmax of x (as a numpy array)
def softmax(x):
    return np.exp(x) / np.sum(np.exp(x))

# AI selects moves from random legal ones
class randAI(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        b = args[0]
        return choice(b.listlegals())

class dumb(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Creates random seed "Droplets", which
# fall downwards to connect the two sides
class dropAI(object):
    def __init__(self, player):
        self.currentseed = None
        self.player = player
        self.randommode = False

    def getEdge(self, b, min=False):
        if not min:
            return [b.board[i][0] for i in range(b.size[0])] if self.player == 1 else \
                    b.board[0]
        else:
            # Return the "Minor" edge
            return [b.board[i][b.size[1] - 1] for i in range(b.size[0])] if self.player == 1 else\
                    b.board[b.size[0] - 1]

    def __call__(self, *args, **kwargs):
        b = args[0]
        if self.randommode:
            return choice(b.listlegals())
        if self.currentseed == None:
            # The "Start" edge
            iedge = self.getEdge(b)
            filled = [not (s == 0) for s in iedge]
            if all(filled):
                self.randommode = True
                return choice(b.listlegals())
            mvables = []
            for i, x in enumerate(iedge):
                if x == 0:
                    mvables += [(0, i)] if self.player == 1 else [(i, 0)]
            newseed = choice(mvables)
            self.currentseed = newseed
            return newseed
        # We have a seed, check for possible branches
        connected = b.adjacent(self.currentseed)
        maximizedir = (lambda x: x[0]) if self.player == 1 else (lambda x: x[1])
        mvables = [c for c in connected if maximizedir(c) > maximizedir(self.currentseed) and b.legal(c)]
        if mvables == []:
            self.currentseed = None
            return self(b)
        newseed = choice(mvables)
        self.currentseed = newseed
        return newseed

class probDropAI(dropAI):
    def __call__(self, *args, **kwargs):
        b = args[0]
        if self.randommode:
            return choice(b.listlegals())
        if self.currentseed == None:
            # The "Start" edge
            iedge = self.getEdge(b)
            filled = [not (s == 0) for s in iedge]
            if all(filled):
                self.randommode = True
                return choice(b.listlegals())
            mvables = []
            for i, x in enumerate(iedge):
                if x == 0:
                    mvables += [(0, i)] if self.player == 1 else [(i, 0)]
            newseed = choice(mvables)
            self.currentseed = newseed
            return newseed
        # We have a seed, check for possible branches
        connected = b.adjacent(self.currentseed)
        maximizedir = (lambda x: x[0]) if self.player == 1 else (lambda x: x[1])
        mvables = [c for c in connected if maximizedir(c) >= maximizedir(self.currentseed) and b.legal(c)]
        if mvables == []:
            self.currentseed = None
            return self(b)
        scores = []
        for x in range(b.size[0]):
            tmp = []
            for y in range(b.size[1]):
                tmp += [0]
            scores += [tmp]
        for index in mvables:
            scores[index[0]][index[1]] += 100
            # Favor choices that go in the right direction
            if maximizedir(index) > maximizedir(self.currentseed):
                scores[index[0]][index[1]] += 100
        probs = softmax(scores)
        alls = []
        for x in range(b.size[0]):
            tmp = []
            for y in range(b.size[1]):
                tmp += [dumb(x,y)]
            alls += [tmp]
        newseed = np.random.choice(np.reshape(np.array(alls), b.size[0]*b.size[1]),
                                   p=np.reshape(np.array(probs), b.size[0]*b.size[1]))
        newseed = (newseed.x, newseed.y)
        self.currentseed = newseed
        return newseed

class doubleProbDropAI(dropAI):

    def __init__(self, player):
        self.seedlings = {'Major': None, 'Minor': None}
        super().__init__(player)

    def __call__(self, *args, **kwargs):
        b = args[0]
        if self.randommode:
            return choice(b.listlegals())
        if self.seedlings['Major'] is None:
            iedge = self.getEdge(b)
            filled = [not (s == 0) for s in iedge]
            if all(filled):
                # TODO: Maybe check out if there are possible seeds later on?
                self.randommode = True
                return choice(b.listlegals())
            mvables = []
            for i, x in enumerate(iedge):
                if x == 0:
                    mvables += [(0, i)] if self.player == 1 else [(i, 0)]
            newseed = choice(mvables)
            self.seedlings['Major'] = newseed
            return newseed
        if self.seedlings['Minor'] is None:
            iedge = self.getEdge(b, min=True)
            filled = [not (s == 0) for s in iedge]
            if all(filled):
                # TODO: Maybe check out if there are possible seeds later on?
                self.randommode = True
                return choice(b.listlegals())
            mvables = []
            for i, x in enumerate(iedge):
                if x == 0:
                    mvables += [(b.size[0] - 1, i)] if self.player == 1 else [(i, b.size[1] - 1)]
            newseed = choice(mvables)
            self.seedlings['Minor'] = newseed
            return newseed
        # We have a seed, check for possible branches
        mjrMoves = [c for c in b.adjacent(self.seedlings['Major']) if b.legal(c)]
        mnrMoves = [c for c in b.adjacent(self.seedlings['Minor']) if b.legal(c)]

        if mjrMoves == []:
            self.seedlings['Major'] = None
            return self(b)
        if mnrMoves == []:
            self.seedlings['Minor'] = None
            return self(b)

        maximizedir = (lambda s, m: s[0] * m) if self.player == 1 else (lambda s, m: s[1] * m)

        scores = []
        for x in range(b.size[0]):
            tmp = []
            for y in range(b.size[1]):
                tmp += [0]
            scores += [tmp]

        for index in mjrMoves:
            scores[index[0]][index[1]] += 100
            # Favor choices that go in the right direction
            if maximizedir(index, 1) > maximizedir(self.seedlings['Major'], 1):
                scores[index[0]][index[1]] += 100

        for index in mnrMoves:
            scores[index[0]][index[1]] += 100
            # Favor choices that go in the right direction
            if maximizedir(index, -1) > maximizedir(self.seedlings['Minor'], -1):
                scores[index[0]][index[1]] += 100
            # TODO: Favor choices which move closer to squares of the same color

        probs = softmax(scores)
        alls = []
        for x in range(b.size[0]):
            tmp = []
            for y in range(b.size[1]):
                tmp += [dumb(x,y)]
            alls += [tmp]
        newseed = np.random.choice(np.reshape(np.array(alls), b.size[0]*b.size[1]),
                                   p=np.reshape(np.array(probs), b.size[0]*b.size[1]))
        newseed = (newseed.x, newseed.y)
        # Kind of hack-y. Probably exploitable
        if newseed in mjrMoves:
            self.seedlings['Major'] = newseed
        else:
            self.seedlings['Minor'] = newseed
        return newseed

class scoreAI(object):
    def __init__(self, player):
        self.player = player
        self.timesmoved = 0

    # Returns a numpy array of the score of each possible move on the board
    def score(self, board):
        return self.emptySB(board)

    # Creates an empty board of zeros which can be used to score
    def emptySB(self, b):
        return np.zeros(b.size)

    def __call__(self, *args, **kwargs):
        b = args[0]
        probs = softmax(self.score(b))
        alls = []
        for x in range(b.size[0]):
            tmp = []
            for y in range(b.size[1]):
                tmp += [dumb(x, y)]
            alls += [tmp]
        ret = np.random.choice(np.reshape(np.array(alls), b.size[0] * b.size[1]),
                                   p=np.reshape(np.array(probs), b.size[0] * b.size[1]))
        ret = (ret.x, ret.y)
        self.timesmoved += 1
        return ret

class hyperScoreAI(scoreAI):

    def __init__(self, player):
        self.easyAI = doubleProbDropAI(player) # Use another AI to start off the game
        super().__init__(player)

    # Return what the board would look like if a certain move was made
    def PU(self, b, pos, color):
        ret = deepcopy(b)
        ret.move(pos, color)
        return ret

    def getLine(self, b, x=0):
        return [b.board[i][x] for i in range(b.size[0])] if self.player == 1 else \
                b.board[x]

    def getChains(self, board, player=None):
        if player is None:
            player = self.player
        shortestbranch = []
        # Find the longest-reaching chains from both directions

        chains = []
        finalchains = []
        visited = []
        # Start the chains
        gl = self.getLine(board, 0)
        for x in range(board.size[self.player-1]):
            if gl[x] == player:
                chains += [[(x, 0)] if player == 1 else [(0, x)]]

        while not chains == []:
            for c in chains:
                lastnode = c[-1]
                chainers = []
                for a in board.adjacent(lastnode):
                    if a in visited:
                        continue
                    try:
                        if board.board[a[0]][a[1]] == player:
                            chainers += [a]
                    except:
                        continue
                if chainers == []:
                    finalchains += [c]
                else:
                    for cnr in chainers:
                        chains += [c + [cnr]]
                        visited += [cnr]
                chains.remove(c)



        if finalchains == []:
            longestchain = [(board.size[0], int(board.size[0]/2))]
        else:
            longestchain = sorted(finalchains, key = lambda a: len(a))[-1]

        # Repeat the process going the other direction
        chains = []
        finalchains = []
        visited = []

        # Start the chains
        gl = self.getLine(board, board.size[0] - 1)
        for x in range(board.size[self.player - 1]):
            if gl[x] == player:
                chains += [[(x, board.size[0])] if player == 1 else [(board.size[0], x)]]

        while not chains == []:
            for c in chains:
                lastnode = c[-1]
                chainers = []
                for a in board.adjacent(lastnode):
                    if a in visited:
                        continue
                    try:
                        if board.board[a[0]][a[1]] == player:
                            chainers += [a]
                    except:
                        continue
                if chainers == []:
                    finalchains += [c]
                else:
                    for cnr in chainers:
                        chains += [c + [cnr]]
                        visited += [cnr]
                chains.remove(c)

        if finalchains == []:
            longestchain2 = [(0, int(board.size[0]/2))]
        else:
            longestchain2 = sorted(finalchains, key=lambda a: len(a))[-1]

        return longestchain, longestchain2

    # HEADS UP: I know this function (and getchains) is a mess. It's a half-decent idea
    # of how well a player is doing though, so I think it's alright for
    # this project, though
    def lightDistance(self, board, player=None):

        #TODO: Adjust values when really close to wall without branches on both sides

        longestchain, longestchain2 = self.getChains(board, player)

        # Start at one of these chains
        # and keep expanding using adjacent() to LEGAL moves
        # that decrease the taxicab difference to the other the most
        totallen = 0
        target = longestchain2[-1][::-1]
        dist = lambda ca: abs(target[0] - ca[0]) + abs(target[1] - ca[1])
        moving = longestchain[-1][::-1]
        while not dist(moving) == 0 and totallen < 30:
            # Move moving closer to the target
            places = [a for a in board.adjacent(moving) if board.legal(a) or a == target]
            if places == []:
                return 100 # I don't like this
            if target in places:
                totallen += 1
                break
            moving = sorted(places, key=dist)[0]
            # if dist(moving) == 1:
            #     # return totallen + 1
            #     return path
            totallen += 1
        # return dist(moving)
        return totallen

    def score(self, board):
        if self.timesmoved > 4:
            alls = []
            for x in range(board.size[0]):
                for y in range(board.size[1]):
                    alls += [(x, y)]
            scrs = self.emptySB(board)
            chain1, chain2 = self.getChains(board)
            mydist = self.lightDistance(board)
            # This is weird
            tmpo = hyperScoreAI(1 if self.player == 2 else 2)
            hisdist = tmpo.lightDistance(board)
            for _cords in alls:
                cords = _cords[::1] # This is annoying
                # All squares get negative bias
                scrs[cords[0]][cords[1]] -= 4
                # Squares get +1 point for being adjacent to a chain
                # for sqr in chain1 + chain2:
                #     if cords in board.adjacent(sqr):
                #         scrs[cords[0]][cords[1]] += 1
                # Squares get +5 points for being adjacent to the head of the chain
                head1 = chain1[-1]
                head2 = chain2[-1]
                if cords in board.adjacent(head1):
                    scrs[cords[0]][cords[1]] += 30

                if cords in board.adjacent(head2):
                    scrs[cords[0]][cords[1]] += 30

                # Now the fancy PU stuff!
                if board.legal(cords):
                    pu = self.PU(board, cords, self.player)
                    mynewdist = self.lightDistance(pu)
                    # Again, weird
                    tmpo_ = hyperScoreAI(1 if self.player == 2 else 2)
                    hisnewdist = tmpo_.lightDistance(pu, 1 if self.player == 2 else 2)

                    if hisnewdist - hisdist > 1:
                        scrs[cords[0]][cords[1]] += 30
                        scrs[cords[0]][cords[1]] += 6 * (hisnewdist - hisdist)
                        # print(str(cords) + ' ' + str(hisnewdist) + ' ' + str(hisdist))

                    if mynewdist < mydist:
                        scrs[cords[0]][cords[1]] += 40
                else:
                    # Illegal squares get huge negative bias
                    scrs[cords[0]][cords[1]] -= 300

            return scrs
        else:
            # There have been less than a few moves so far
            # Just use the starting AI
            mv = self.easyAI(board)
            scrs = self.emptySB(board)
            scrs[mv[0]][mv[1]] = 200
            return scrs