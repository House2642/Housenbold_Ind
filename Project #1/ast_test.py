from openai import OpenAI
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

def test_expression_reconstruction(expr: Expr, test_words: bool = False) -> bool:
    system_message = """
    You are a mathematical expression builder. Given a mathematical expression in either:
    1. Standard notation (e.g., "(5 + 3) * 2")
    2. Word format (e.g., "the product of the sum of 5 and 3 and 2")

    Generate Python code using these classes:
    - Number(value): Creates a number node
    - Add(left, right): Adds two expressions
    - Sub(left, right): Subtracts two expressions
    - Mul(left, right): Multiplies two expressions
    - Div(left, right): Divides two expressions

    CRITICAL RULES:
    1. Each operation (Add, Sub, Mul, Div) MUST have EXACTLY two arguments
    2. For expressions with multiple operations, nest them properly
    3. Never use more than 2 arguments per operation
    4. ALWAYS wrap number literals with Number()
    5. For complex expressions, build them from inside out

    Examples:
    "5 minus 1" → Sub(Number(5), Number(1))
    "5 plus 1" → Add(Number(5), Number(1))
    "2 plus 3 plus 4" → Add(Add(Number(2), Number(3)), Number(4))
    "multiply 2 times 3 times 4" → Mul(Mul(Number(2), Number(3)), Number(4))
    "the quotient of the sum of 2 and 3 and 4" → Div(Add(Number(2), Number(3)), Number(4))

    IMPORTANT: 
    - All operations must be binary (exactly two arguments)
    - Chain operations from left to right using proper nesting
    - Always write out the complete expression
    - Never use ... or ellipsis
    - Only respond with valid Python code using these classes, nothing else
    - Make sure to not use quotes around the final expression output
    - Every number must be wrapped in Number()
    """

    try:
        str_expr = str(expr)
        words = expr.to_words()

        # Test string representation
        response_str = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": str_expr}
            ],
            temperature=0.0
        )

        if test_words:
            # Test word representation
            response_words = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": words}
                ],
                temperature=0.0
            )

            expression_code_str = response_str.choices[0].message.content.strip()
            expression_code_words = response_words.choices[0].message.content.strip()

            expr_nums = eval(expression_code_str, {"Number": Number, "Add": Add, "Sub": Sub, "Mul": Mul, "Div": Div})
            expr_words = eval(expression_code_words, {"Number": Number, "Add": Add, "Sub": Sub, "Mul": Mul, "Div": Div})

            try:
                if (expr_nums.eval() != expr.eval() or str(expr_nums) != str(expr)
                    or expr_words.eval() != expr.eval() or expr_words.to_words() != expr.to_words()):
                    print("\nOriginal expression:", str_expr)
                    print("Word format:", words)
                    print("\nAPI Response for string format:", expression_code_str)
                    print("API Response for word format:", expression_code_words)
                    print("Constructed expression from string:", str(expr_nums))
                    print("Constructed expression from words:", expr_words.to_words())
                    return False
                return True
            except ZeroDivisionError:
                return True
        else: 
           expression_code_str = response_str.choices[0].message.content.strip()
           expr_nums = eval(expression_code_str, {"Number": Number, "Add": Add, "Sub": Sub, "Mul": Mul, "Div": Div})
           try:
               if (expr_nums.eval() != expr.eval() or str(expr_nums) != str(expr)):
                    print("\nOriginal expression:", str_expr)
                    print("\nAPI Response for string format:", expression_code_str)
                    print("Constructed expression from string:", str(expr_nums))
                    return False
               return True
           except ZeroDivisionError:
               return True
        
    except Exception as e:
        print(f"\nError processing expression: {str(expr)}")
        print("\nOriginal expression:", str_expr)
        print("\nAPI Response for string format:", expression_code_str)
        print(f"Error: {str(e)}")
        return False

def generate_random_ast(max_depth=4) -> Expr:
    import random
    
    # Base case: always use Number constructor
    if max_depth <= 1:
        return Number(random.randint(1, 10))
    
    # For non-base cases, always create a nested expression
    operators = [Add, Sub, Mul, Div]
    op = random.choice(operators)
    
    # Both left and right should be expressions
    left = generate_random_ast(max_depth - 1)
    right = generate_random_ast(max_depth - 1)
    
    # Avoid division by zero
    if op == Div and isinstance(right, Number) and right.value == 0:
        right = Number(random.randint(1, 10))
            
    return op(left, right)

# Test with 25 random ASTs
def run_tests(num_tests=25, test_words=False):
    successes = 0
    failures = 0
    
    for i in range(num_tests):
        print(f"\nTest {i + 1}/{num_tests}")
        ast = generate_random_ast()
        if test_expression_reconstruction(ast):
            successes += 1
        else:
            failures += 1
    
    print(f"\nFinal Results:")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Success rate: {(successes/num_tests)*100:.2f}%")

if __name__ == "__main__":
    run_tests()
