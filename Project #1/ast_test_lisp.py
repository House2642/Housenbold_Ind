from openai import OpenAI
import matplotlib.pyplot as plt
import random
from lisp_ast import tokenize, read_from_tokens, eval, convert_to_infix, parse

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

def test_expression_reconstruction(lisp_expr: str) -> bool:
    system_message = """
    You are a mathematical expression builder. Given a mathematical expression in standard notation (e.g., "(5 + 3) * 2"),
    generate Lisp code using these functions:
    - (number value): Creates a number node
    - (add left right): Adds two expressions
    - (sub left right): Subtracts two expressions
    - (mul left right): Multiplies two expressions
    - (div left right): Divides two expressions

    CRITICAL RULES:
    1. Each operation MUST have EXACTLY two arguments
    2. For expressions with multiple operations, nest them properly
    3. Never use more than 2 arguments per operation
    4. ALWAYS wrap number literals with number
    5. For complex expressions, build them from inside out

    Examples:
    "5 - 1" → (sub (number 5) (number 1))
    "5 + 1" → (add (number 5) (number 1))
    "2 + 3 + 4" → (add (add (number 2) (number 3)) (number 4))
    "2 * 3 * 4" → (mul (mul (number 2) (number 3)) (number 4))
    "(2 + 3) / 4" → (div (add (number 2) (number 3)) (number 4))

    IMPORTANT: 
    - All operations must be binary (exactly two arguments)
    - Chain operations from left to right using proper nesting
    - Always write out the complete expression
    - Never use ... or ellipsis
    - Only respond with valid Lisp code using these functions, nothing else
    """

    try:
        # Convert Lisp expression to infix notation for GPT
        infix_expr = convert_to_infix(lisp_expr)
        print(f"Original Lisp: {lisp_expr}")
        print(f"Infix expression: {infix_expr}")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": infix_expr}
            ],
            temperature=0.0
        )

        generated_expr = response.choices[0].message.content.strip()
        print(f"Generated Lisp: {generated_expr}")

        # Compare the generated expression with the original
        if generated_expr != lisp_expr or eval(parse(generated_expr)) != eval(parse(lisp_expr)):
            return False
        return True

    except Exception as e:
        print(f"\nError processing expression: {lisp_expr}")
        print(f"Error: {str(e)}")
        return False

def generate_random_ast(max_depth=4) -> str:
    if max_depth <= 1:
        return f"(number {random.randint(1, 10)})"
    
    operators = ['add', 'sub', 'mul', 'div']
    op = random.choice(operators)
    
    left = generate_random_ast(max_depth - 1)
    right = generate_random_ast(max_depth - 1)
    
    # Avoid division by zero by checking the right operand
    if op == 'div':
        tokens = tokenize(right)
        ast = read_from_tokens(tokens)
        if eval(ast) == 0:
            right = f"(number {random.randint(1, 10)})"
            
    return f"({op} {left} {right})"

def run_tests(num_tests=25):
    depths = range(1, 8)  # K values from 2 to 3
    success_rates = []
    
    for k in depths:
        print(f"\nTesting depth K={k}")
        successes = 0
        failures = 0
        
        for i in range(num_tests):
            print(f"\nTest {i + 1}/{num_tests} for K={k}")
            ast = generate_random_ast(max_depth=k)
            if test_expression_reconstruction(ast):
                successes += 1
            else:
                failures += 1
                
        success_rate = (successes/num_tests)*100
        success_rates.append(success_rate)
        print(f"\nResults for K={k}:")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Success rate: {success_rate:.2f}%")
    
    # Create and save the graph
    plt.figure(figsize=(10, 6))
    plt.plot(depths, success_rates, marker='o')
    plt.xlabel('AST Depth (K)')
    plt.ylabel('Success Rate (%)')
    plt.title('Lisp Expression Reconstruction Success Rate vs Tree Depth')
    plt.grid(True)
    plt.savefig('lisp_ast_success_rates.png')
    plt.close()
    
    print("\nGraph has been saved as 'lisp_ast_success_rates.png'")

if __name__ == "__main__":
    run_tests() 