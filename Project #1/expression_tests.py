from openai import OpenAI
import random
from expressions import Number, Add, Sub, Mul, Div, Expr
from datetime import datetime, timedelta

# Set random seed for reproducibility
random.seed(42)

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

    # Recursively build the code format string
def get_code_format(e):
    if isinstance(e, Number):
        return f"Number({e.value})"
    return f"{e.__class__.__name__}({get_code_format(e.left)}, {get_code_format(e.right)})"
    

def test_gpt_expression_conversion(num_tests: int, depth: int, model: str = "gpt-3.5-turbo") -> tuple[float, float]:
    """
    Tests GPT's ability to convert random expressions of given depth, returns success rates.
    
    Args:
        num_tests (int): Number of random expressions to test
        depth (int): Maximum depth of generated expressions
        input_token_cost_per_million (float): Cost per 1M input tokens (default: $1.50 for GPT-3.5-turbo)
        output_token_cost_per_million (float): Cost per 1M output tokens (default: $2.00 for GPT-3.5-turbo)
        
    Returns:
        tuple[float, float]: (value_match_rate, code_match_rate)
    """
    system_message = open("prompts/exp_gpt_prompt.txt", "r").read()

    value_matches = 0
    code_matches = 0
    total_evaluable = 0
    total_parseable = 0  # New counter for expressions that can be parsed
    total_tokens = 0

    for i in range(num_tests):
        expr = generate_random_expression(depth)
        expression = str(expr)
        print(f"\nTest {i+1}/{num_tests}")
        print(f"Testing expression: {expression}")
        
        try:
            response = client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": expression}
                ],
                temperature=0.0
            )
            
            # Track token usage
            total_tokens += response.usage.prompt_tokens + response.usage.completion_tokens
            
            expression_code = response.choices[0].message.content.strip()
            print(f"Generated code: {expression_code}")
            
            # Always attempt string matching
            original_code = get_code_format(expr)
            total_parseable += 1  # Count this as a parseable attempt
            if original_code == expression_code:
                code_matches += 1
                print("String representation match!")
            else:
                print("String representation mismatch!")
                print(f"Original code format: {original_code}")
                print(f"Generated code format: {expression_code}")
            
            try:
                # Try to parse and evaluate
                generated_expr = eval(expression_code, {"Number": Number, "Add": Add, "Sub": Sub, "Mul": Mul, "Div": Div})
                original_result = expr.eval()
                generated_result = generated_expr.eval()
                
                # If we get here, both expressions were successfully evaluated
                total_evaluable += 1
                
                if original_result == generated_result:
                    value_matches += 1
                    print(f"Evaluation match: both = {original_result}")
                else:
                    print(f"Evaluation mismatch!")
                    print(f"Original expression evaluates to: {original_result}")
                    print(f"Generated expression evaluates to: {generated_result}")
                    
            except ZeroDivisionError:
                print("Evaluation skipped: Division by zero")
            except Exception as e:
                print(f"Error in parsing or evaluation: {str(e)}")
                
        except Exception as e:
            print(f"API or other error: {str(e)}")
    
    # Calculate success rates
    value_success_rate = value_matches / total_evaluable if total_evaluable > 0 else 0.0
    code_success_rate = code_matches / total_parseable if total_parseable > 0 else 0.0
    
    print(f"\nOverall Results:")
    print(f"Total tests: {num_tests}")
    print(f"Successfully parsed: {total_parseable}")
    print(f"Successfully evaluated: {total_evaluable}")
    print(f"Value match success rate: {value_success_rate:.2%}")
    print(f"Code match success rate: {code_success_rate:.2%}")
    print(f"Total tokens used: {total_tokens}")
    
    return value_success_rate, code_success_rate, total_tokens, total_evaluable

# Example usage:
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("\nTesting GPT expression conversion across depths 1-6:")
    
    depths = range(1, 7)
    value_rates = []
    code_rates = []
    total_tokens = 0
    evaluable_counts = []
    
    for depth in depths:
        print(f"\nTesting depth {depth}:")
        value_rate, code_rate, tokens, total_evaluable = test_gpt_expression_conversion(25, depth)
        value_rates.append(value_rate)
        code_rates.append(code_rate)
        total_tokens += tokens
        evaluable_counts.append(total_evaluable)
    
    # Calculate total cost at the end
    input_token_cost_per_million: float = 1.50,
    output_token_cost_per_million: float = 2.00,
    total_cost = (total_tokens * 0.50 / 1_000_000) + (total_tokens * 1.50 / 1_000_000)
    print(f"\nTotal cost for all tests: ${total_cost:.6f}")
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(depths, value_rates, marker='o')
    plt.title('Evaluation Accuracy vs Expression Depth')
    plt.xlabel('Expression Depth')
    plt.ylabel('Accuracy')
    for i, (d, n) in enumerate(zip(depths, evaluable_counts)):
        plt.annotate(f'depth {d}, n={n}', (depths[i], value_rates[i]), 
                    textcoords="offset points", xytext=(0,10), ha='center')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(depths, code_rates, marker='o')
    plt.title('String Matching Accuracy vs Expression Depth')
    plt.xlabel('Expression Depth')
    plt.ylabel('Accuracy')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()