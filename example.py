from hypothesis import given, strategies as st

@given(st.integers())
def test_integers(n):
    print(f"called with {n}")
    assert isinstance(n, int)

test_integers()