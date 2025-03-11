# https://norvig.com/lispy.html

from typing import Union, List as PyList

import math
import operator as op

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = Union[int, float]
Atom = Union[Symbol, Number]
List = PyList
Exp = Union[Atom, "List"]  # Using string for forward reference
Env = dict             # A Scheme environment (defined below) 
                        
def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program: str) -> Exp:
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update({
        'number': lambda x: x,  # Simply returns the number
        'add': op.add,
        'sub': op.sub,
        'mul': op.mul,
        'div': op.truediv,
    })
    return env

global_env = standard_env()

def eval(x: Exp, env=global_env) -> Exp:
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        return env[x]
    elif isinstance(x, Number):    # constant number
        return x                
    else:                         # procedure call
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

def convert_to_infix(expr_str: str) -> str:
    """Convert a Lisp expression to infix notation"""
    expr = parse(expr_str)
    
    def _convert(x: Exp, is_outer: bool = True) -> str:
        if isinstance(x, Number):
            return str(x)
        
        # For procedure calls
        if len(x) > 0:
            op = x[0]
            op_map = {
                'add': '+',
                'sub': '-',
                'mul': '*', 
                'div': '/'
            }
            
            if op == 'number':
                return str(x[1])
                
            if op in op_map:
                left = _convert(x[1], False)
                right = _convert(x[2], False)
                op_symbol = op_map[op]
                
                # For mul/div, wrap operands if they are add/sub expressions
                if op in ['mul', 'div']:
                    # Check if left operand is an add/sub expression
                    if isinstance(x[1], list) and x[1][0] in ['add', 'sub']:
                        left = f"({left})"
                    # Check if right operand is an add/sub expression
                    if isinstance(x[2], list) and x[2][0] in ['add', 'sub']:
                        right = f"({right})"
                    result = f"{left} {op_symbol} {right}"
                else:
                    # For add/sub, no need to wrap operands
                    result = f"{left} {op_symbol} {right}"
                
                return result
                
        return str(x)
        
    return _convert(expr)

def test_infix_conversion():
    """Test the infix notation converter with various expressions"""
    test_cases = [
        # Basic number tests
        ("(number 5)", "5"),
        
        # Basic arithmetic tests
        ("(add (number 2) (number 3))", "2 + 3"),
        ("(sub (number 5) (number 3))", "5 - 3"), 
        ("(mul (number 4) (number 2))", "4 * 2"),
        ("(div (number 10) (number 2))", "10 / 2"),
        
        # Nested expression tests
        ("(add (mul (number 2) (number 3)) (number 4))", "2 * 3 + 4"),
        ("(mul (add (number 2) (number 3)) (sub (number 10) (number 5)))", "(2 + 3) * (10 - 5)"),
        
        # Complex nested expressions
        ("(add (mul (sub (number 10) (number 5)) (number 2)) (div (number 20) (number 4)))", 
         "(10 - 5) * 2 + 20 / 4")
    ]

    passed = 0
    failed = 0

    for expr_str, expected in test_cases:
        try:
            result = convert_to_infix(expr_str)
            if result == expected:
                print(f"PASS: {expr_str} → {result}")
                passed += 1
            else:
                print(f"FAIL: {expr_str}, expected {expected}, got {result}")
                failed += 1
                
        except Exception as e:
            print(f"ERROR: {expr_str} raised {str(e)}")
            failed += 1

    print(f"\nTest Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")

def test_lisp_eval():
    """Test the Lisp evaluator with various expressions"""
    test_cases = [
        # Basic number tests
        ("(number 5)", 5),
        
        # Basic arithmetic tests
        ("(add (number 2) (number 3))", 5),
        ("(sub (number 5) (number 3))", 2), 
        ("(mul (number 4) (number 2))", 8),
        ("(div (number 10) (number 2))", 5),
        
        # Nested expression tests
        ("(add (mul (number 2) (number 3)) (number 4))", 10),
        ("(mul (add (number 2) (number 3)) (sub (number 10) (number 5)))", 25),
        ("(div (mul (number 4) (number 6)) (add (number 2) (number 2)))", 6),
        
        # Complex nested expressions
        ("(add (mul (sub (number 10) (number 5)) (number 2)) (div (number 20) (number 4)))", 15),
    ]

    passed = 0
    failed = 0

    for expr_str, expected in test_cases:
        try:
            tokens = tokenize(expr_str)
            ast = read_from_tokens(tokens)
            result = eval(ast)
            
            if result == expected:
                print(f"PASS: {expr_str} = {result}")
                passed += 1
            else:
                print(f"FAIL: {expr_str}, expected {expected}, got {result}")
                failed += 1
                
        except Exception as e:
            print(f"ERROR: {expr_str} raised {str(e)}")
            failed += 1

    print(f"\nTest Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")


if __name__ == "__main__":
    test_infix_conversion()
    test_lisp_eval()

    