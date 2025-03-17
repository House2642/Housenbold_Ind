import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from lisp_tests import test_gpt_expression_conversion as test_lisp
from expression_tests import test_gpt_expression_conversion as test_expr

def run_model_comparison_tests(models: List[str], num_tests: int = 25):
    """
    Runs comparison tests across different GPT models.
    
    Args:
        models: List of model IDs to test (e.g., ["gpt-3.5-turbo", "gpt-4"])
        num_tests: Number of tests to run per depth level
    """
    print("\nRunning model comparison tests across depths 1-6:")
    
    depths = range(1, 7)
    results: Dict[str, Dict[str, List[float]]] = {}
    evaluable_counts: Dict[str, Dict[str, List[int]]] = {}
    total_costs: Dict[str, float] = {}
    
    for model in models:
        results[model] = {
            'lisp_value_rates': [],
            'lisp_code_rates': [],
            'expr_value_rates': [],
            'expr_code_rates': []
        }
        evaluable_counts[model] = {
            'lisp': [],
            'expr': []
        }
        total_tokens = 0
        
        # Run tests for each depth
        for depth in depths:
            print(f"\nTesting {model} at depth {depth}:")
            
            print("Testing Lisp expressions...")
            lisp_value, lisp_code, lisp_tokens, lisp_eval = test_lisp(
                num_tests, depth, model=model
            )
            results[model]['lisp_value_rates'].append(lisp_value)
            results[model]['lisp_code_rates'].append(lisp_code)
            evaluable_counts[model]['lisp'].append(lisp_eval)
            
            print("\nTesting Standard expressions...")
            expr_value, expr_code, expr_tokens, expr_eval = test_expr(
                num_tests, depth, model=model
            )
            results[model]['expr_value_rates'].append(expr_value)
            results[model]['expr_code_rates'].append(expr_code)
            evaluable_counts[model]['expr'].append(expr_eval)
            
            total_tokens += lisp_tokens + expr_tokens
        
        # Calculate cost based on model
        if model == "gpt-4":
            total_costs[model] = (total_tokens * 0.03 / 1_000) + (total_tokens * 0.06 / 1_000)
        else:  # gpt-3.5-turbo
            total_costs[model] = (total_tokens * 0.0015 / 1_000) + (total_tokens * 0.002 / 1_000)
            
        print(f"\nTotal cost for {model}: ${total_costs[model]:.6f}")
        
        # Print results for each depth
        print("\nResults by depth:")
        for i, depth in enumerate(depths):
            print(f"\nDepth {depth}:")
            print(f"Lisp evaluation accuracy: {results[model]['lisp_value_rates'][i]:.2%}")
            print(f"Lisp string matching accuracy: {results[model]['lisp_code_rates'][i]:.2%}")
            print(f"Expression evaluation accuracy: {results[model]['expr_value_rates'][i]:.2%}")
            print(f"Expression string matching accuracy: {results[model]['expr_code_rates'][i]:.2%}")

if __name__ == "__main__":
    models = ["gpt-3.5-turbo"]  # Add more models as needed
    run_model_comparison_tests(models)