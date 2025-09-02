from ternkernel.adapters.numpy_bridge import safe_div

def test_safe_div_scalar_zero():
    assert safe_div(1, 0) == 0

def test_safe_div_list_zero():
    out = safe_div([1,2,3],[1,0,2])
    assert out == [1.0, 0, 1.5]
