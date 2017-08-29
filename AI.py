from random import choice

# AI selects moves from random legal ones
class randAI(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        b = args[0]
        return choice(b.listlegals())

# Creates random seed "Droplets", which
# fall downwards to connect the two sides
class dropAI(object):
    def __init__(self, player):
        self.currentseed = None
        self.player = player
        self.randommode = False

    def __call__(self, *args, **kwargs):
        b = args[0]
        if self.randommode:
            return choice(b.listlegals())
        if self.currentseed == None:
            # The "Start" edge
            # TODO: Make it switch-up which edge it takes
            iedge = [b.board[i][0] for i in range(b.size[0])] if self.player == 1 else \
                    b.board[0]
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