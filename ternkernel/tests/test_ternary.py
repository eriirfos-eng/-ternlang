import itertools
from ternkernel.core.ternary import VALID, meet, join, neg, imp_godel, de_morgan_left, de_morgan_right

def test_de_morgan():
    for a,b in itertools.product(VALID, repeat=2):
        assert de_morgan_left(a,b)
        assert de_morgan_right(a,b)

def test_residuation():
    for a,b in itertools.product(VALID, repeat=2):
        lhs = meet(a, imp_godel(a,b))
        assert lhs <= b
