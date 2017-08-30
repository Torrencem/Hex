from random import choice

import numpy as np


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