from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional

class NodeType(Enum):
    Program = "Program"
    
    # Statements
    ExpressionStatement = "ExpressionStatement"
    VarStatement = "VarStatement"
    FunctionStatement = "FunctionStatement"
    BlockStatement = "BlockStatement"
    ReturnStatement = "ReturnStatement"
    AssignStatement = "AssignStatement"
    
    # Expressions
    InfixExpression = "InfixExpression"
    
    # Literals
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"
    IdentifierLiteral = "IdentifierLiteral"
    
class Node(ABC):
    @abstractmethod
    def type(self) -> NodeType:
        pass
    
    @abstractmethod
    def json(self) -> Dict:
        pass


class Statement(Node):
    pass

class Expression(Node):
    pass

class Program(Node):
    def __init__(self) -> None:
        self.statements: List[Statement] = []
        
    def type(self) -> NodeType:
        return NodeType.Program
    
    def json(self) -> Dict:
        return {
            "type": self.type().value,
            "statements": [{stmt.type().value: stmt.json()} for stmt in self.statements]
        }
        
# region Statements
class ExpressionStatement(Statement):
    def __init__(self, expr: Optional[Expression] = None) -> None:
        self.expr = expr
        
    def type(self) -> NodeType:
        return NodeType.ExpressionStatement
    
    def json(self) -> Dict:
        if self.expr is None: raise
        return {
            "type": self.type().value,
            "expr": self.expr.json() # type: ignore
        }
        
class VarStatement(Statement):
    def __init__(self, name: Optional[Expression] = None, value: Optional[Expression] = None,
                 value_type: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        self.value_type = value_type
        
    def type(self) -> NodeType:
        return NodeType.VarStatement
    
    def json(self) -> dict:
        if self.name is None or self.value is None: raise
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "value": self.value.json(),
            "value_type": self.value_type
        }
        
class BlockStatement(Statement):
    def __init__(self, statements: Optional[List[Statement]] = None) -> None:
        self.statements = statements if statements is not None else []

    def type(self) -> NodeType:
        return NodeType.BlockStatement
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }
        
class ReturnStatement(Statement):
    def __init__(self, return_value: Optional[Expression] = None) -> None:
        self.return_value = return_value

    def type(self) -> NodeType:
        return NodeType.ReturnStatement
    
    def json(self) -> dict:
        if self.return_value is None: raise
        return {
            "type": self.type().value,
            "return_value": self.return_value.json()
        }
        
class FunctionStatement(Statement):
    def __init__(self, parameters: List = [], 
                 body: Optional[BlockStatement] = None, 
                 name = None, 
                 return_type: Optional[str] = None) -> None:
        self.parameters = parameters
        self.body = body
        self.name = name
        self.return_type = return_type

    def type(self) -> NodeType:
        return NodeType.FunctionStatement
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "return_type": self.return_type,
            "parameters": [p.json() for p in self.parameters],
            "body": self.body.json() if self.body else {}
        }
        
class AssignStatement(Statement):
    def __init__(self, ident: Optional[Expression] = None, 
                 right_value: Optional[Expression] = None) -> None:
        self.ident = ident
        self.right_value = right_value

    def type(self) -> NodeType:
        return NodeType.AssignStatement
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "ident": self.ident.json() if self.ident else None,
            "right_value": self.right_value.json() if self.right_value else None
        }
# endregion

# region Expressions
class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node: Optional[Expression] = None) -> None:
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node
        
    def type(self) -> NodeType:
        return NodeType.InfixExpression
    
    def json(self) -> Dict:
        if self.right_node is None: raise
        
        return {
            "type": self.type().value,
            "left_node": self.left_node.json(),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }
# endregion

# region Literals
class IntegerLiteral(Expression):
    def __init__(self, value: Optional[int] = None) -> None:
        self.value = value
    
    def type(self) -> NodeType:
        return NodeType.IntegerLiteral
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }
    
class FloatLiteral(Expression):
    def __init__(self, value: Optional[float] = None) -> None:
        self.value = value
    
    def type(self) -> NodeType:
        return NodeType.FloatLiteral
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }
        
class IdentifierLiteral(Expression):
    def __init__(self, value: Optional[str] = None) -> None:
        self.value = value
    
    def type(self) -> NodeType:
        return NodeType.IdentifierLiteral
    
    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }
# endregion
