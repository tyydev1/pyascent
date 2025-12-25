from typing import Dict, List, Optional, Tuple
from llvmlite import ir # type: ignore

from AST import Node, NodeType, Program, Expression
from AST import ExpressionStatement, VarStatement, BlockStatement, FunctionStatement, ReturnStatement, AssignStatement, IfStatement
from AST import InfixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral

from Environment import Environment

class Compiler:
    def __init__(self) -> None:
        self.type_map: Dict[str, ir.Type] = {
            'int': ir.IntType(32),
            'flo': ir.FloatType(),
            'bool': ir.IntType(1)
        }
        
        self.module: ir.Module = ir.Module('main')
        
        self.builder: ir.IRBuilder = ir.IRBuilder()
        
        self.env: Environment = Environment()
        
        # Temporary keeping track of errors
        self.errors: List[str] = []
        
        self.__initialize_builtins()

    def __initialize_builtins(self) -> None:
        def __init_booleans() -> tuple[ir.GlobalVariable, ir.GlobalVariable]:
            bool_type: ir.Type = self.type_map['bool']

            true_var = ir.GlobalVariable(self.module, bool_type, 'true')
            true_var.initializer = ir.Constant(bool_type, 1)
            true_var.global_constant = True

            false_var = ir.GlobalVariable(self.module, bool_type, 'false')
            false_var.initializer = ir.Constant(bool_type, 0)
            false_var.global_constant = True

            return true_var, false_var

        true_var, false_var = __init_booleans()
        self.env.define('true', true_var, true_var.type)
        self.env.define('false', false_var, false_var.type)
        
    def compile(self, node: Node) -> None:
        match node.type():
            case NodeType.Program:
                self.__visit_program(node) # type: ignore

            # Statements
            case NodeType.ExpressionStatement:
                self.__visit_expression_statement(node) # type: ignore
            case NodeType.VarStatement:
                self.__visit_var_statement(node) # type: ignore
            case NodeType.FunctionStatement:
                self.__visit_function_statement(node) # type: ignore
            case NodeType.BlockStatement:
                self.__visit_block_statement(node) # type: ignore
            case NodeType.ReturnStatement:
                self.__visit_return_statement(node) # type: ignore
            case NodeType.AssignStatement:
                self.__visit_assign_statement(node) # type: ignore
            case NodeType.IfStatement:
                self.__visit_if_statement(node) # type: ignore
            
            # Expressions
            case NodeType.InfixExpression:
                self.__visit_infix_expression(node) # type: ignore
        
        
    # region Visit Methods
    def __visit_program(self, node: Program) -> None:
        for stmt in node.statements:
            self.compile(stmt)
        
    # region Statements
    def __visit_expression_statement(self, node: ExpressionStatement) -> None:
        self.compile(node.expr) # type: ignore
        
    def __visit_var_statement(self, node: VarStatement) -> None:
        name: str = node.name.value # type: ignore
        value: Expression = node.value # type: ignore
        value_type: str = node.value.type # type: ignore # TODO: implement this fred
        
        value, Type = self.__resolve_value(node=value)
        
        if self.env.lookup(name) is None:
            # Define and allocate the variable
            ptr = self.builder.alloca(Type)
            
            # Storing the value
            self.builder.store(value, ptr)
            
            # Add the variable to the environment
            self.env.define(name, ptr, Type)
        else:
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)
            
    def __visit_block_statement(self, node: BlockStatement) -> None:
        for stmt in node.statements:
            if self.builder.block.terminator is not None:
                break
            self.compile(stmt)
            
    def __visit_return_statement(self, node: ReturnStatement) -> None:
        value: Expression = node.return_value # type: ignore
        value, Type = self.__resolve_value(value)
        
        if self.builder.block.terminator is None:
            self.builder.ret(value)

    def __visit_function_statement(self, node: FunctionStatement) -> None:
        name: str = node.name.value # type: ignore
        body: BlockStatement = node.body # type: ignore
        params: List[IdentifierLiteral] = node.parameters
        
        # Keep track of the names of each parameter
        param_names: list[str] = [p.value for p in params] # type: ignore # TODO

        # Keep track of the types for each parameter
        param_types: list[ir.Type] = []  # TODO

        return_type: ir.Type = self.type_map[node.return_type] # type: ignore

        fnty: ir.FunctionType = ir.FunctionType(return_type, param_types)
        func: ir.Function = ir.Function(self.module, fnty, name=name)

        block: ir.Block = func.append_basic_block(f'{name}_entry')

        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)

        previous_env = self.env

        self.env = Environment(parent=self.env)
        self.env.define(name, func, return_type)

        self.compile(body)

        self.env = previous_env
        self.env.define(name, func, return_type)

        self.builder = previous_builder
        
    def __visit_assign_statement(self, node: AssignStatement) -> None:
        name: str = node.ident.value # type: ignore
        value: Expression = node.right_value # type: ignore

        value, Type = self.__resolve_value(value)

        if self.env.lookup(name) is None:
            self.errors.append(f"CompilerError: identifier '{name}' has not been declared before it was re-assigned")
        else:
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)
            
    def __visit_if_statement(self, node: IfStatement) -> None:
        condition = node.condition
        consequence = node.consequence
        alternative = node.alternative
        
        test, _ = self.__resolve_value(condition) # type: ignore
        
        if alternative is None:
            with self.builder.if_then(test):
                self.compile(consequence) # type: ignore
        else:
            # Manually create blocks
            then_block = self.builder.append_basic_block('if.then')
            else_block = self.builder.append_basic_block('if.else')
            merge_block = self.builder.append_basic_block('if.merge')
            
            # Create conditional branch
            self.builder.cbranch(test, then_block, else_block)
            
            # Compile then block
            self.builder.position_at_end(then_block)
            self.compile(consequence) # type: ignore
            if self.builder.block.terminator is None:
                self.builder.branch(merge_block)
            
            # Compile else block
            self.builder.position_at_end(else_block)
            self.compile(alternative) # type: ignore
            if self.builder.block.terminator is None:
                self.builder.branch(merge_block)
            
            # Continue in merge block
            self.builder.position_at_end(merge_block)
    # endregion
    
    # region Expressions
    def __visit_infix_expression(self, node: InfixExpression):
        operator: str = node.operator
        left_value, left_type = self.__resolve_value(node.left_node)
        right_value, right_type = self.__resolve_value(node.right_node) # type: ignore
        
        value = None
        Type = None
        if isinstance(right_type, ir.IntType) and isinstance(left_type, ir.IntType):
            Type = self.type_map['int']
            match operator:
                case '+':
                    value = self.builder.add(left_value, right_value)
                case '-':
                    value = self.builder.sub(left_value, right_value)
                case '*':
                    value = self.builder.mul(left_value, right_value)
                case '/':
                    value = self.builder.sdiv(left_value, right_value)
                case '%':
                    value = self.builder.srem(left_value, right_value)
                case '^':
                    # TODO
                    pass
                case '<':
                    value = self.builder.icmp_signed('<', left_value, right_value)
                    Type = ir.IntType(1)
                case '<=':
                    value = self.builder.icmp_signed('<=', left_value, right_value)
                    Type = ir.IntType(1)
                case '>':
                    value = self.builder.icmp_signed('>', left_value, right_value)
                    Type = ir.IntType(1)
                case '>=':
                    value = self.builder.icmp_signed('>=', left_value, right_value)
                    Type = ir.IntType(1)
                case '==':
                    value = self.builder.icmp_signed('==', left_value, right_value)
                    Type = ir.IntType(1)
                
        elif isinstance(right_type, ir.FloatType) and isinstance(left_type, ir.FloatType):
            Type = ir.FloatType()
            match operator:
                case '+':
                    value = self.builder.fadd(left_value, right_value)
                case '-':
                    value = self.builder.fsub(left_value, right_value)
                case '*':
                    value = self.builder.fmul(left_value, right_value)
                case '/':
                    value = self.builder.fdiv(left_value, right_value)
                case '%':
                    value = self.builder.frem(left_value, right_value)
                case '^':
                    # TODO
                    pass
                case '<':
                    value = self.builder.fcmp_ordered('<', left_value, right_value)
                    Type = ir.IntType(1)
                case '<=':
                    value = self.builder.fcmp_ordered('<=', left_value, right_value)
                    Type = ir.IntType(1)
                case '>':
                    value = self.builder.fcmp_ordered('>', left_value, right_value)
                    Type = ir.IntType(1)
                case '>=':
                    value = self.builder.fcmp_ordered('>=', left_value, right_value)
                    Type = ir.IntType(1)
                case '==':
                    value = self.builder.fcmp_ordered('==', left_value, right_value)
                    Type = ir.IntType(1)
                    
        return value, Type
    # endregion
    
    # endregion
    
    # region Helper Methods
    def __resolve_value(self, node: Expression) -> Tuple[ir.Value, ir.Type]:
        match node.type():
            case NodeType.IntegerLiteral:
                node: IntegerLiteral = node # type: ignore
                value, Type = node.value, self.type_map['int'] # type: ignore
                return ir.Constant(Type, value), Type
            case NodeType.FloatLiteral:
                node: FloatLiteral = node # type: ignore
                value, Type = node.value, self.type_map['flo'] # type: ignore
                return ir.Constant(Type, value), Type
            case NodeType.IdentifierLiteral:
                node: IdentifierLiteral = node # type: ignore
                ptr, Type = self.env.lookup(node.value) # type: ignore
                return self.builder.load(ptr), Type
            case NodeType.BooleanLiteral:
                node: BooleanLiteral = node # type: ignore
                return ir.Constant(ir.IntType(1), 1 if node.value else 0), ir.IntType(1) # type: ignore
            
            # Expression Values
            case NodeType.InfixExpression:
                return self.__visit_infix_expression(node) # type: ignore
            
        return (None, None)
    # endregion
