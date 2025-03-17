from openai import OpenAI
import random
from lisp_ast import tokenize, read_from_tokens, eval, convert_to_infix, parse
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

def generate_random_lisp_expression(max_depth=4) -> str:
    """
    Generates a random Lisp expression string with a maximum depth.
    """
    if max_depth <= 1:
        return f"(number {random.randint(1, 10)})"
    
    operators = ['add', 'sub', 'mul', 'div']
    op = random.choice(operators)
    
    left = generate_random_lisp_expression(max_depth - 1)
    right = generate_random_lisp_expression(max_depth - 1)
    
    # For division, ensure we don't divide by zero
    if op == 'div':
        try:
            right_val = eval(parse(right))
            if right_val == 0:
                right = f"(number {random.randint(1, 10)})"
        except:
            right = f"(number {random.randint(1, 10)})"
            
    return f"({op} {left} {right})"

def test_gpt_expression_conversion(num_tests: int, depth: int, model: str = "gpt-3.5-turbo") -> tuple[float, float, int, int]:
    """
    Tests GPT's ability to convert random Lisp expressions of given depth.
    
    Returns:
        tuple[float, float, int, int]: (value_match_rate, code_match_rate, total_tokens, total_evaluable)
    """
    system_message = open("prompts/lisp_gpt_prompt.txt").read()

    value_matches = 0
    code_matches = 0
    total_evaluable = 0
    total_parseable = 0
    total_tokens = 0

    for i in range(num_tests):
        lisp_expr = generate_random_lisp_expression(depth)
        infix_expr = convert_to_infix(lisp_expr)
        print(f"\nTest {i+1}/{num_tests}")
        print(f"Original Lisp: {lisp_expr}")
        print(f"Infix expression: {infix_expr}")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": infix_expr}
                ],
                temperature=0.0
            )
            
            total_tokens += response.usage.prompt_tokens + response.usage.completion_tokens
            generated_expr = response.choices[0].message.content.strip()
            print(f"Generated Lisp: {generated_expr}")
            
            # Always attempt string matching
            total_parseable += 1
            if generated_expr == lisp_expr:
                code_matches += 1
                print("String representation match!")
            else:
                print("String representation mismatch!")
                print(f"Original Lisp: {lisp_expr}")
                print(f"Generated Lisp: {generated_expr}")
            
            try:
                # Try to parse and evaluate both expressions
                original_result = eval(parse(lisp_expr))
                generated_result = eval(parse(generated_expr))
                
                total_evaluable += 1
                
                if original_result == generated_result:
                    value_matches += 1
                    print(f"Evaluation match: both = {original_result}")
                else:
                    print(f"Evaluation mismatch!")
                    print(f"Original evaluates to: {original_result}")
                    print(f"Generated evaluates to: {generated_result}")
                    
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
    
    # Calculate total cost
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