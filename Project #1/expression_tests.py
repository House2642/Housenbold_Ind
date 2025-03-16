from openai import OpenAI
import random
from expressions import Number, Add, Sub, Mul, Div, Expr

def read_api_key(filename="../api/openaikey.txt"):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Please create a {filename} file with your OpenAI API key")
    except Exception as e:
        raise Exception(f"Error reading API key: {e}")

# Setup OpenAI client
api_key = read_api_key()
client = OpenAI(api_key=api_key)

def generate_random_expression(max_depth=4) -> Expr:
    """
    Generates a random mathematical expression tree with a maximum depth.
    
    Args:
        max_depth (int): Maximum depth of the expression tree
        
    Returns:
        Expr: A randomly generated expression
    """
    # Base case: at max depth return a number
    if max_depth <= 1:
        return Number(random.randint(1, 10))
    
    # Choose a random operator
    operators = [Add, Sub, Mul, Div]
    op = random.choice(operators)
    
    # Generate left and right expressions with reduced depth
    left = generate_random_expression(max_depth - 1)
    right = generate_random_expression(max_depth - 1)
    
    # For division, ensure we don't divide by zero
    if op == Div:
        # If right side evaluates to 0, replace it with a random number
        try:
            if right.eval() == 0:
                right = Number(random.randint(1, 10))
        except:
            # If evaluation fails, try generating a new right expression
            # that doesn't cause division by zero
            right = generate_random_expression(max_depth - 1)
            while True:
                try:
                    if right.eval() == 0:
                        right = generate_random_expression(max_depth - 1)
                    else:
                        break
                except:
                    right = generate_random_expression(max_depth - 1)
            
    return op(left, right)

def test_expression(expr: Expr):
    """
    Test a single expression by printing its string representation and evaluated result
    """
    print(f"Expression: {str(expr)}")
    try:
        result = expr.eval()
        print(f"Evaluation: {result}")
    except ZeroDivisionError:
        print("Evaluation failed: Division by zero")
    except Exception as e:
        print(f"Evaluation failed: {str(e)}")
    print()

# Example usage:
if __name__ == "__main__":
    print("Testing simple expressions:")
    test_expression(Add(Number(5), Number(3)))  # 5 + 3
    test_expression(Mul(Number(4), Sub(Number(7), Number(2))))  # 4 * (7 - 2)
    
    print("\nTesting random expressions of increasing depth:")
    for depth in range(1, 5):
        print(f"\nDepth {depth}:")
        for _ in range(3):
            expr = generate_random_expression(max_depth=depth)
            test_expression(expr)




