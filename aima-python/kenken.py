from csp import *
import operator
import re

#___________________________________________________________________________
"""#KenKen

#KenKen puzzle input format :
#To fully define a KenKen puzzle we only need to define its cages and the grid size. To define one cage , we need 
#to know the variables that a given cage consists of , the operator of the cage and the result of the operation .(Actually,
#these are the attributes of the Cage class).
#So,the input format consists of from cages which are delimited by the character '|' 
#Note: the first node is not a cage but it is the grid size (only the one dimension).
#Each cage is defined in the following format : [result_of_operation][operator][list_of_variables_seperated_by_comma] .
#Note: If a cage consists of only one variable , then the operator is character '?' .  """

easy11 = '4|16*0,4,5|1-1,2|1?3|2/6,10|9+7,11,15|1-8,12|3?9|3-13,14'

hard11 = '6|60*0,1,7|2?6|10+2,3,8|14+4,5,11,17|5+9,10|8+12,13,18|48*14,15,20|3?16|24*19,25,31|12+21,27,33,34|6?35|1-22,23|1-28,29|2/24,30|6+26,32'

extra_hard = '9|20*0,1,2|5-4,5|30+3,12,21,30|19+6,15,16|120*7,8,17|17+9,10,11,19|17+13,14,23|2-18,27|42*20,29|2-22,31|13+24,33,42|4-25,26|11+34,35,44|72*28,37,38|1-39,40|1-41,32|13+36,45,46|3+47,56|1-54,55|45*48,49|2-50,51|1-52,43|10+57,58|64*59,60,61|3-62,53|5-63,72|1-64,73|160*65,66,74,75|4-67,68|1?76|56*69,70,71|2/78,77|18*79,80'
#Operator symbols are mapped to operator functions implemented in operator
#module .For example , if we need to calculate a+b we can use operator.add(a,b)
op_dict = { 
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '?': None
}

#A Cage consists of:
    #i)one list of variables (the variables that define the cage).
    #ii)one operator [possible operators are /,+,*,-].
    #ii)one integer which is the result that the cage should satisfy .
class Cage:
    def __init__(self, variables, op , result):
        self.variables = variables
        self.op = op_dict[op]
        self.string_op = op         #operator as a string.
        self.result = result
    def getOp(self):
        return self.string_op
    def getOpfunc(self):
        return self.op
    def has_solution(self,remain_var, curr_val, currdoms):
        """ Recursively check if cage has a solution when one variable(the variable 
        that is not present in remain_var list) has value curr_val.
        remain_var is a list that initially has all cage's variables except the one we are examining .
        currdoms are the current domains of the cage's variables.
        If this func returns True it means that the cage has a solution.
        If returns None then there is no solution.
        This func only works for operators * , +  and equality symbol ('?').
        """
        if len(remain_var) == 0:
            return curr_val == self.result
        for value in currdoms[remain_var[0]]:
            boolvar = self.has_solution(remain_var[1:],self.op(curr_val,int(value)) ,currdoms)
            if boolvar == True :    #if we find at least one solution , exit 
                return True
        return False

    def has_solution_Div_Sub(self,var, curr_val, currdoms):
        """Checks if a cage with '/' or '-' operators has solution when we  have
        the value of either one variable or both of them (curr_val) .
        var is a list that holds either one variable or is empty.
        Note: We check if a/b==result and if b/a==result.Same for - operator."""
        if len(var) == 0 :
            if self.getOp() == '-' :
                return curr_val == self.result or curr_val== -1 * self.result
            if self.getOp() == '/' :
                return curr_val == self.result or curr_val== 1 / self.result
        else:
            for value in currdoms[var[0]]:
                return self.op(curr_val,int(value))== self.result or self.op(int(value),curr_val)== self.result 
        return False

    def getVars(self):
        return self.variables

class KenKen(CSP):
    def __init__(self,puzzle):
        splited = puzzle.split('|')
        n = int(splited[0])
        splited = splited[1:]
        self.cages = self.parsePuzzle(splited)
        self.RN = list(range(n))
        self.Cell = itertools.count().__next__ 
        self.bgrid = [[self.Cell() for x in self.RN] for y in self.RN]
        self.rows = self.bgrid    # rows are same as bgrid 
        self.cols = list(zip(*self.bgrid))
        self.neighbors = {v :set() for v in sum(self.rows,[])} 
        self.cages_vars = [cage.getVars() for cage in self.cages]
        for unit in map(set, self.rows + self.cols + self.cages_vars):
            for v in unit:
                self.neighbors[v].update(unit-{v})
       
        #Create a string = '1,2..N' where n*n is the size of the grid.
        possible_val = ''.join(str(v) for v in range(1,n+1))
        #domains are initially all posible values i.e '1,2..N'
        self.domains = {var : possible_val for var in sum(self.rows,[])}
        CSP.__init__(self,None,self.domains,self.neighbors,self.KenKen_constraints)
        #Override CSP attribute curr_domains. Here, we definitely want to use it.
        self.curr_domains = {v: list(self.domains[v]) for v in sum(self.rows,[])}

    def parsePuzzle(self,splited):
        """Parse the puzzle with with the help of regex. 
        Create a list of cages and return it."""
        p = re.compile("\*|\/|\+|\-|\?")
        v = re.compile("[^,]+")
        cage_list = []
        for cage in splited:
            res = p.search(cage)
            ope = res.group()
            end = res.end()
            start = res.start()
            cage_res = int(cage[:start])
            lst = v.findall(cage[end:])
            lst = [int(var) for var in lst]
            cage_list.append(Cage(lst,ope,cage_res))
        return cage_list

    def findCage(self,var):
        """Given a variable , find its cage"""
        for cage in self.cages:
            if var in cage.getVars():
                return cage

    def KenKen_constraints(self,A,a,B,b) :
        """Check if two values are the same and belong in the same row or column.
        If not,check if A belongs in a cage with only one variable (A) and if yes,
        check if value 'a' is solution of the cage.
        .Lastly,check if A and B belong in the same cage and test 
        if cage has_solution with values a and b."""
        Bcage = self.findCage(B)
        Acage = self.findCage(A)
        if a == b and (self.existInSublist(A,B,self.rows) or self.existInSublist(A,B,self.cols)):
            return False
        elif len(Acage.getVars()) == 1:
            Acage_vars =  Acage.getVars()[:]
            Acage_vars.remove(A)
            return Acage.has_solution(Acage_vars,int(a),self.curr_domains)         
        elif Acage == Bcage :
            Bcage_vars = Bcage.getVars()[:]
            Bcage_vars.remove(B)
            Bcage_vars.remove(A)
            if Bcage.getOp() == '+' or Bcage.getOp() ==  '*':
                return Bcage.has_solution(Bcage_vars,Bcage.getOpfunc()(int(b),int(a)) ,self.curr_domains)         
            else :
                return Bcage.has_solution_Div_Sub(Bcage_vars,Bcage.getOpfunc()(int(b),int(a)) ,self.curr_domains)
        else :
            return True

    def existInSublist(self,var1,var2,l):
        """check if two vars exist in a list of a list of lists.
        Used in KenKen_constraints"""
        for sub in l:
            if (var1 in sub) and (var2 in sub):
                return True
        return False
    def getDomains(self):
        return self.curr_domains




e = KenKen(easy11)
e2 = KenKen(hard11)
e3 = KenKen(extra_hard)
print(AC3(e3))
print(min_conflicts(e2))
#print(backtracking_search(e))
#print(backtracking_search(e,select_unassigned_variable=mrv))
#print(backtracking_search(e2,select_unassigned_variable=mrv,inference=forward_checking))
#print (e.getDomains().values())
#print(backtracking_search(e,select_unassigned_variable=mrv))
