from openai import OpenAI
from expressions import Number, Add, Sub, Mul, Div, Expr

client = OpenAI()

system_message = """
You are a mathematical expression builder. Given a mathematical question, generate Python code using these classes:
- Number(value): Creates a number node
- Add(left, right): Adds two expressions
- Sub(left, right): Subtracts two expressions
- Mul(left, right): Multiplies two expressions
- Div(left, right): Divides two expressions

Examples:
Simple:
"5 minus 1" → Sub(Number(5), Number(1))
"5 plus 1" → Add(Number(5), Number(1))

Complex:
"start with 15 subtract 10 then multiply by 4" → Mul(Sub(Number(15), Number(10)), Number(4))
"multiply 4 by the sum of 2 and 3" → Mul(Number(4), Add(Number(2), Number(3)))

IMPORTANT: Always write out the complete expression. Never use ... or ellipsis.
Only respond with valid Python code using these classes, nothing else.
Make sure to not use quotes around the final expression output.
"""

print("\nEnter a mathematical expression (e.g., 'start with 15 subtract 10 then multiply by 4')")
question = input("Expression: ")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": question}
    ],
    temperature=0.0
)

expression_code = response.choices[0].message.content.strip()
print("\nConstructed expression:", expression_code)

expr = eval(expression_code, {"Number": Number, "Add": Add, "Sub": Sub, "Mul": Mul, "Div": Div})
print("Type of expr:", type(expr))
result = expr.eval()
print("Result:", result)
