from GameCore import *
from BadAI import randAI, hyperScoreAI

# Start an untimed game between two AI functions
def qgame(f1, f2):
    b = board()
    turn = 1
    while b.boardstate() == 'No Win':
        b.move((f1 if turn == 1 else f2)(b, turn), turn)
        turn = 2 if turn == 1 else 1
    return b.boardstate()

def randqgame():
    f1 = randAI()
    f2 = randAI()
    qgame(f1, f2)


def relativeEval(a1, a2, n:int=100):
    scores = {}
    scores['a1 first'] = {'a1':0, 'a2':0}
    scores['a2 first'] = {'a1':0, 'a2':0}
    for first in [1, 2]:
        s = 'a1 first' if first == 1 else 'a2 first'
        for i in range(n):
            status = qgame(*((a1, a2) if first == 1 else (a2, a1)))
            if status == '1 Win':
                scores[s]['a1' if first == 1 else 'a2'] += 1
            elif status == '2 Win':
                scores[s]['a2' if first == 1 else 'a1'] += 1
            print(i)
    return scores

if __name__ == '__main__':
    a1 = randAI()
    a2 = hyperScoreAI(2)
    print(relativeEval(a1, a2, n=25))