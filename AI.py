from random import choice

import numpy as np

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
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
        return [b.board[i][0] for i in range(b.size[0])] if self.player == 1 else \
                    b.board[0]

    def __call__(self, *args, **kwargs):
        b = args[0]
        if self.randommode:
            return choice(b.listlegals())
        if self.currentseed == None:
            # The "Start" edge
            # TODO: Make it switch-up which edge it takes
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
            self.currentseed = newseed
            return newseed
        # We have a seed, check for possible branches
        connected = b.adjacent(self.currentseed)
        # TODO: Adjust this if it is going from the opposite edge
        maximizedir = (lambda x: x[0]) if self.player == 1 else (lambda x: x[1])
        # TODO: Also maybe make this >= ? Or make it optional, that would be cool
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
            # TODO: Make it switch-up which edge it takes
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
            self.currentseed = newseed
            return newseed
        # We have a seed, check for possible branches
        connected = b.adjacent(self.currentseed)
        # TODO: Adjust this if it is going from the opposite edge
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