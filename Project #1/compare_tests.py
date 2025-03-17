import matplotlib.pyplot as plt
from lisp_tests import test_gpt_expression_conversion as test_lisp
from expression_tests import test_gpt_expression_conversion as test_expr

def run_comparison_tests(num_tests=25):
    print("\nRunning comparison tests across depths 1-6:")
    
    depths = range(1, 7)
    lisp_value_rates = []
    lisp_code_rates = []
    expr_value_rates = []
    expr_code_rates = []
    lisp_evaluable = []
    expr_evaluable = []
    total_tokens = 0
    
    # Run both sets of tests
    for depth in depths:
        print(f"\nTesting depth {depth}:")
        
        print("Testing Lisp expressions...")
        lisp_value, lisp_code, lisp_tokens, lisp_eval = test_lisp(num_tests, depth)
        lisp_value_rates.append(lisp_value)
        lisp_code_rates.append(lisp_code)
        lisp_evaluable.append(lisp_eval)
        
        print("\nTesting Standard expressions...")
        expr_value, expr_code, expr_tokens, expr_eval = test_expr(num_tests, depth)
        expr_value_rates.append(expr_value)
        expr_code_rates.append(expr_code)
        expr_evaluable.append(expr_eval)
        
        total_tokens += lisp_tokens + expr_tokens

    # Calculate total cost
    total_cost = (total_tokens * 0.50 / 1_000_000) + (total_tokens * 1.50 / 1_000_000)
    print(f"\nTotal cost for all tests: ${total_cost:.6f}")
    
    # Create comparison plots
    plt.figure(figsize=(12, 5))
    
    # Value comparison plot
    plt.subplot(1, 2, 1)
    plt.plot(depths, lisp_value_rates, 'b-o', label='Lisp', alpha=0.7)
    plt.plot(depths, expr_value_rates, 'r-o', label='Expression', alpha=0.7)
    plt.title('Evaluation Accuracy Comparison')
    plt.xlabel('Expression Depth')
    plt.ylabel('Accuracy')
    
    # Add annotations for sample counts
    for i, (d, ln, en) in enumerate(zip(depths, lisp_evaluable, expr_evaluable)):
        plt.annotate(f'n={ln}', (depths[i], lisp_value_rates[i]), 
                    textcoords="offset points", xytext=(0,10), 
                    ha='center', color='blue')
        plt.annotate(f'n={en}', (depths[i], expr_value_rates[i]), 
                    textcoords="offset points", xytext=(0,-15), 
                    ha='center', color='red')
    
    plt.grid(True)
    plt.legend()
    
    # Code match comparison plot
    plt.subplot(1, 2, 2)
    plt.plot(depths, lisp_code_rates, 'b-o', label='Lisp', alpha=0.7)
    plt.plot(depths, expr_code_rates, 'r-o', label='Expression', alpha=0.7)
    plt.title('String Matching Accuracy Comparison')
    plt.xlabel('Expression Depth')
    plt.ylabel('Accuracy')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_comparison_tests() 