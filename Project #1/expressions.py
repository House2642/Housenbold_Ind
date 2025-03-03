from abc import ABC, abstractmethod

class Expr(ABC):
    @abstractmethod
    def eval(self)->int:
        pass
        
    @abstractmethod
    def __str__(self)->str:
        pass

    @abstractmethod
    def to_words(self) -> str:
        pass

class Number(Expr):
    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError("Value must be an integer")
        self.value = value

    def eval(self)->int:
        return self.value
        
    def __str__(self)->str:
        return str(self.value)
    
    def to_words(self) -> str:
        return str(self.value)

class Add(Expr):
    def __init__(self, left: Expr, right: Expr):
        if not (isinstance(left, Expr) and isinstance(right, Expr)):
            raise TypeError("Both arguments must be Expr instances")
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() + self.right.eval()
        
    def __str__(self)->str:
        # Add/Sub need parentheses when they're inside other operations
        left_str = f"({str(self.left)})" if isinstance(self.left, (Add, Sub)) else str(self.left)
        right_str = f"({str(self.right)})" if isinstance(self.right, (Add, Sub)) else str(self.right)
        return f"{left_str} + {right_str}"
    
    def to_words(self) -> str:
        return f"the sum of {self.left.to_words()} and {self.right.to_words()}"

class Sub(Expr):
    def __init__(self, left: Expr, right: Expr):
        if not (isinstance(left, Expr) and isinstance(right, Expr)):
            raise TypeError("Both arguments must be Expr instances")
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() - self.right.eval()
        
    def __str__(self)->str:
        # Add/Sub need parentheses when they're inside other operations
        left_str = f"({str(self.left)})" if isinstance(self.left, (Add, Sub)) else str(self.left)
        right_str = f"({str(self.right)})" if isinstance(self.right, (Add, Sub)) else str(self.right)
        return f"{left_str} - {right_str}"
    
    def to_words(self) -> str:
        return f"the difference of {self.left.to_words()} and {self.right.to_words()}"

class Mul(Expr):
    def __init__(self, left: Expr, right: Expr):
        if not (isinstance(left, Expr) and isinstance(right, Expr)):
            raise TypeError("Both arguments must be Expr instances")
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() * self.right.eval()
        
    def __str__(self)->str:
        # Always wrap the operands in parentheses if they're not simple numbers
        left_str = str(self.left) if isinstance(self.left, Number) else f"({str(self.left)})"
        right_str = str(self.right) if isinstance(self.right, Number) else f"({str(self.right)})"
        return f"{left_str} * {right_str}"
    
    def to_words(self) -> str:
        return f"the product of {self.left.to_words()} and {self.right.to_words()}"

class Div(Expr):
    def __init__(self, left: Expr, right: Expr):
        if not (isinstance(left, Expr) and isinstance(right, Expr)):
            raise TypeError("Both arguments must be Expr instances")
        self.left = left
        self.right = right

    def eval(self)->int:
        if self.right.eval() == 0:
            raise ZeroDivisionError("Division by zero")
        return int(self.left.eval() / self.right.eval())
        
    def __str__(self)->str:
        # Always wrap the operands in parentheses if they're not simple numbers
        left_str = str(self.left) if isinstance(self.left, Number) else f"({str(self.left)})"
        right_str = str(self.right) if isinstance(self.right, Number) else f"({str(self.right)})"
        return f"{left_str} / {right_str}"
    
    def to_words(self) -> str:
        return f"the quotient of {self.left.to_words()} and {self.right.to_words()}"

def test(num1: Expr, num2: Expr):
    add = Add(num1, num2)
    sub = Sub(num1, num2)
    mul = Mul(num1, num2)
    div = Div(num1, num2)
    print(add.eval())
    print(sub.eval())
    print(mul.eval())
    print(div.eval())

def test2(num1: Expr, num2: Expr, num3: Expr):
    print("test2")
    layered = Add(num1, Mul(num2, num3))
    print(layered.eval())
    layered2 = Add(Sub(num1, Div(num1, num2)), layered)
    print(layered2.eval())
    last = Add(Sub(Mul(Number(15), Number(25)), Number(3)), Number(5))
    Step_1 = Mul(Number(15), Number(25))
    Step_2 = Sub(Step_1, Number(3))
    Step_3 = Add(Step_2, Number(5))

def test3(num1: Expr, num2: Expr, num3: Expr):
    print("test3")
    # Test string representations of expressions
    simple_add = Add(num1, num2)
    print(f"Simple addition: {simple_add}")
    print(f"Simple addition: {simple_add.to_words()}")
    nested_mul = Mul(num1, Add(num2, num3))
    print(f"Nested multiplication: {nested_mul}")
    print(f"Nested multiplication: {nested_mul.to_words()}")    
    complex_expr = Div(Sub(Mul(num1, num2), num3), Number(2))
    print(f"Complex expression: {complex_expr}")
    print(f"Complex expression: {complex_expr.to_words()}")
    # Test that parentheses are added correctly for compound expressions
    compound = Add(Mul(num1, num2), Div(num2, num3))
    print(f"Compound expression: {compound}")
    print(f"Compound expression: {compound.to_words()}")
    
    compound2 = Add(Sub(Mul(num1, Add(num2,num2)), num3), Number(5))
    print(f"Compound expression: {compound2}")
    print(f"Compound expression: {compound2.to_words()}")

    compound3 = Add(Sub(Mul(num1, num2), num3), Number(5))
    print(f"Compound expression: {compound3}")
    print(f"Compound expression: {compound3.to_words()}")

    
#test(Number(10), Number(2))
test2(Number(15), Number(25), Number(3))
test3(Number(10), Number(2), Number(3))