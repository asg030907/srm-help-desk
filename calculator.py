"""
calculator.py
Arithmetic tool using a restricted AST evaluator — no eval() on raw
strings, so the agent can't be tricked into executing arbitrary code
through a "calculate this" prompt.
"""

import ast
import operator

from crewai.tools import tool

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


@tool("Calculator")
def calculate(expression: str) -> str:
    """
    Evaluates a basic arithmetic expression (+, -, *, /, %, ** and
    parentheses) and returns the numeric result as a string. Use this
    instead of doing math yourself — it guarantees correctness for
    anything beyond trivial mental arithmetic.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as exc:  # noqa: BLE001 — surface the error to the agent
        return f"Could not evaluate '{expression}': {exc}"
