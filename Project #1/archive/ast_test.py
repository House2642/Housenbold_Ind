from openai import OpenAI
from expressions import Number, Add, Sub, Mul, Div, Expr
import matplotlib.pyplot as plt

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
    system_message = open("prompts/exp_gpt_prompt.txt").read()
    expression_code_str = None  # Initialize the variable before try block
    
    try:
        str_expr = str(expr)
        words = expr.to_words()

        # Test string representation
        response_str = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": str_expr}
            ],
            temperature=0.0
        )
        expression_code_str = response_str.choices[0].message.content.strip()

        if test_words:
            # Test word representation
            response_words = client.chat.completions.create(
                model="o1-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": words}
                ],
                temperature=0.0
            )

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
        if expression_code_str:  # Only print if we got a response
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

# Test with 25 random ASTs for each depth K from 1 to 7
def run_tests(num_tests=25, test_words=True):  
    depths = range(1, 8)  # K values from 1 to 7
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
    plt.title('AST Reconstruction Success Rate vs Tree Depth')
    plt.grid(True)
    plt.savefig('ast_success_rates.png')
    plt.close()
    
    print("\nGraph has been saved as 'ast_success_rates.png'")

if __name__ == "__main__":
    run_tests(num_tests=25, test_words=False)