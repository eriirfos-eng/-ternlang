from ternlang.math.divide import divide

def test_div0_collapse():
    res, state = divide(5, 0)
    assert res == 0 and state == "TEND"

def test_sign_classify():
    assert divide(-2,1)[1] == "REFRAIN"
    assert divide(0,1)[1]  == "TEND"
    assert divide(2,1)[1]  == "AFFIRM"
