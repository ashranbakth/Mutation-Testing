import ast
import astor
import astpretty
import sys
import copy
from random import *
import random

def Parse(path):
    # parse the target program to ast
     source = open(target_path).read()
     return ast.parse(source, target_path)




class Count_Compare(ast.NodeTransformer):
    # Magic here:
    # you should know when you need generic_visit(), how visit() works?
    # How visit_calssname() works? How do they work together?

    def visit_Compare(self, node):
        global number_of_comparisons 

        if(isinstance(node.ops[0], ast.GtE)):
            new_node = ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.LtE)):
            new_node = ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.Gt)):
            new_node = ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.Lt)):
            new_node = ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators)
            number_of_comparisons += 1

        return node

class Count_BinaryOp(ast.NodeTransformer):

    def visit_BinOp(self, node):
        global number_of_binary

        if(isinstance(node.op, ast.Add)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Sub)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Mult)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Div)):
            number_of_binary += 1

        return node

       
        

class Count_FunctionCall(ast.NodeTransformer):
    def visit_If(self, node):
        global if_found 
        if_found = 1
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        #print("function_call line: ", node.lineno)
        global number_of_call, if_found
        if(if_found == 1):
            if_found = 0
            return node
        number_of_call += 1
        return node

    def visit_Assign(self, node):
        #print("assign line: ", node.lineno)
        global number_of_assign
        number_of_assign += 1
        return node

    

class Rewrite_Compare(ast.NodeTransformer):

    def visit_Compare(self, node):

        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            ##print("Rewrite compare Line: ", node.lineno)
            if(isinstance(node.ops[0], ast.GtE)):
                new_node = ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.LtE)):
                new_node = ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.Gt)):
                new_node = ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.Lt)):
                new_node = ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators)
                return new_node

        return node

class Rewrite_BinaryOp(ast.NodeTransformer):

    def visit_BinOp(self, node):
        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            ##print("Rewrite_binary Line: ", node.lineno)
            if(isinstance(node.op, ast.Add)):
                node.op = ast.Sub()
            elif(isinstance(node.op, ast.Sub)):
                node.op = ast.Add()
            elif(isinstance(node.op, ast.Mult)):
                node.op = ast.FloorDiv()
            elif(isinstance(node.op, ast.Div) or isinstance(node.op, ast.FloorDiv)):
                node.op = ast.Mult()

        return node

class Rewrite_FunctionCall(ast.NodeTransformer):



    def visit_If(self, node):
        global if_found 
        if_found = 1
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        global visit_count, visit_target, if_found
        visit_count += 1
        if(if_found == 1):
            if_found = 0
            return node
        if(visit_count == visit_target):
            ##print("call line: ", node.lineno)
            return ast.Pass()
        return node
            #print("function_call line: ", node.lineno)
            #return ast.copy_location(ast.Call(func=1, args=None), node)

    def visit_Assign(self, node):
        
        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            ##print("assign line: ", node.lineno)
            return ast.copy_location(ast.Assign(targets=node.targets, value=ast.NameConstant(value=1)), node)
        return node
        
    

        
        
        

    # def visit_Compare(self, node):
    #     if node.ops[0] == ast.GtE():
    #         print ("GtE")
    #         print(node.lineno)
    #         #newnode = ast.UnaryOp(ast.Lt(), ast.Num(ast.Num().n, ast.Num().lineno, ast.Num().col_offset), node.lineno, node.col_offset)
    #         newnode = ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators)
    #         return newnode



# print(sys.argv[0])
# print(sys.argv[1])
# print(sys.argv[2])
#target_path = "./test.py"
target_path = "./" + sys.argv[1]

number_of_mutants = int(sys.argv[2])
mutants_made = 0

tree = Parse(target_path)
#astpretty.pprint(tree)

if_found = 0
assign_found = 0
number_of_comparisons = 0
number_of_binary = 0
number_of_assign = 0
number_of_call = 0
number_of_functioncall = 0

Count_Compare().visit(tree)
Count_BinaryOp().visit(tree)
Count_FunctionCall().visit(tree)
number_of_functioncall = number_of_assign + number_of_call

mutant_combo_list = list()

visit_target = 0
visit_count = 0
seed = 0


while(mutants_made < number_of_mutants):
        ## creating random numbers for which nodes to mutate from comparison, binaryop, and function call
        random.seed(seed)
        seed += 1
        comparison_mutant = randint(1,number_of_comparisons)
        binary_mutant = randint(1,number_of_binary)
        functioncall_mutant = randint(1,number_of_functioncall)
        
        
        if([comparison_mutant, binary_mutant, functioncall_mutant] not in mutant_combo_list):
            # Make this mutant if it is not already made (mutant_combo_list)
            mutant_combo_list.append([comparison_mutant, binary_mutant, functioncall_mutant])
            
            new_tree = copy.deepcopy(tree)
            visit_target = comparison_mutant
            visit_count = 0
            new_tree = Rewrite_Compare().visit(new_tree)
            visit_target = binary_mutant
            visit_count = 0
            new_tree = Rewrite_BinaryOp().visit(new_tree)
            #visit_target = functioncall_mutant
            visit_target = functioncall_mutant
            visit_count = 0
            if_found = 0
            new_tree = Rewrite_FunctionCall().visit(new_tree)
            # Create a new mutant file called 0.py, 1.py, .....
            file_name = str(mutants_made) + ".py"
            #print(file_name)
            f = open(file_name, "w+")
            f.write(astor.to_source(new_tree))

            # Increment mutants_made to show in process of a new mutant being made
            mutants_made += 1
            ##print("mutants made: ", mutants_made)
             ## REMOVE THIS
            
            
    


# print("List: ", mutant_combo_list)




# print(astor.to_source(new_tree))
# ##print(astor.to_source(main_copy_tree)
# print("comparisons: ", number_of_comparisons)
# print("binary: ", number_of_binary)
# print("function assign: ", number_of_assign)
# print("function call: ", number_of_call)
# print("total function call: ", number_of_functioncall)


