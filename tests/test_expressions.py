from hypothesis import given, settings
from hypothesis import strategies as st


""" 
Partitioning:
With partitioning, we would have had to manually identify input classes
and write one or a few tests per partition. This coverage would only be good
for the partitions we think should be defined. However, Hypothesis
generates the input across the entire grammer automatically which finds cases that
we might not have thought of when partitioning.

Logical Expressions:
With logical expression, we would have had to focused on making sure that 
every boolean condition and branch in the code was covered. This would 
require us to understand the implementation of the code. However,
with Hypothesis, it would really only know the grammar rather than the implementation.
So this would supplement the logical expression and provide more varied testing.

Mutation Testing:
With mutation testing, this would check whether a test suite was strong enough
to detect small changes in the code. This would test for quality, but not input diversity.
So Hypothesis would be a good complement to mutation testing by providing a wide range of 
inputs that could potentially trigger the mutations, thus helping to identify weaknesses 
in the test suite that mutation testing might reveal.

"""

def digit() -> st.SearchStrategy[str]:
    """Matches: digit = '0' | '1' | ... | '9' """
    return st.sampled_from("0123456789")


def constant() -> st.SearchStrategy[str]:
    """Matches: constant = digit {digit}
    One or more digits joined into a string (e.g. '0', '42', '317').
    """
    return st.lists(digit(), min_size=1, max_size=5).map(lambda ds: "".join(ds))


def factor() -> st.SearchStrategy[str]:
    """Matches: factor = constant | '(' expression ')'
    Uses st.deferred to handle the recursive reference to expression().
    """
    return st.one_of(
        constant(),
        st.deferred(expression).map(lambda e: f"({e})")
    )


def term() -> st.SearchStrategy[str]:
    """Matches: term = factor { ('*' | '/') factor }
    One or more factors joined by * or /.
    """
    operator = st.sampled_from(["*", "/"])
    return st.lists(factor(), min_size=1, max_size=4).flatmap(
        lambda factors: st.lists(
            operator, min_size=len(factors) - 1, max_size=len(factors) - 1
        ).map(lambda ops: _interleave(factors, ops))
    )


def expression() -> st.SearchStrategy[str]:
    """Matches: expression = term { ('+' | '-') term }
    One or more terms joined by + or -.
    """
    operator = st.sampled_from(["+", "-"])
    return st.lists(term(), min_size=1, max_size=4).flatmap(
        lambda terms: st.lists(
            operator, min_size=len(terms) - 1, max_size=len(terms) - 1
        ).map(lambda ops: _interleave(terms, ops))
    )


def _interleave(operands: list, operators: list) -> str:
    """Helper: interleave ['a','b','c'] with ['+','-'] -> 'a+b-c'"""
    if not operators:
        return operands[0]
    result = operands[0]
    for op, operand in zip(operators, operands[1:]):
        result += op + operand
    return result


def expr() -> st.SearchStrategy[str]:
    """Top-level strategy — produces a valid expression string."""
    return expression()


@given(expr())
@settings(max_examples=50)
def test_print(expression: str):
    print(expression)