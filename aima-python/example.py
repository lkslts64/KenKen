

class A:
    def __init__(self):
        self.var1=4
        print (self.var1)
    def add(self,x,y):
        print (self.var1)
        return x+y


class B(A):
    def __init__(self):
        self.var1 = 5
        print (self.var1)
    




a = A()
b = B()

b.add(3,3)


