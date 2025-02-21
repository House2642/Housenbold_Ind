from abc import ABC, abstractmethod

class Expr(ABC):
    def eval(self) :
        pass

class Number(Expr):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value
    
class Add(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self):
        return self.left.eval() + self.right.eval()
    
class Sub(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self):
        return self.left.eval() - self.right.eval()
    
class Mul(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self):
        return self.left.eval() * self.right.eval()
    
class Div(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self):
        return self.left.eval() / self.right.eval()

def test(num1, num2):
    add = Add(num1, num2)
    sub = Sub(num1, num2)
    mul = Mul(num1, num2)
    div = Div(num1, num2)
    print(add.eval())
    print(sub.eval())
    print(mul.eval())
    print(div.eval())

test(Number(10), Number(2))