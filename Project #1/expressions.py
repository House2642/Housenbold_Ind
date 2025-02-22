from abc import ABC, abstractmethod

class Expr(ABC):
    def eval(self)->int:
        pass

class Number(Expr):
    def __init__(self, value):
        self.value = value

    def eval(self)->int:
        return self.value
    
class Add(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() + self.right.eval()
    
class Sub(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() - self.right.eval()
    
class Mul(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self)->int:
        return self.left.eval() * self.right.eval()
    
class Div(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self)->int:
        return  int( self.left.eval() / self.right.eval())

def test(num1, num2):
    add = Add(num1, num2)
    sub = Sub(num1, num2)
    mul = Mul(num1, num2)
    div = Div(num1, num2)
    print(add.eval())
    print(sub.eval())
    print(mul.eval())
    print(div.eval())

def test2(num1, num2, num3):
    print("test2")
    layered = Add(num1, Mul(num2, num3))
    print(layered.eval())
    layered2 = Add(Sub(num1, Div(num1, num2)), layered)
    print(layered2.eval())
#test(Number(10), Number(2))
#test2(Number(10), Number(2), Number(3))