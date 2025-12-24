from enum import Enum
from typing import Any, Dict, List

class TokenType(Enum):
    # Special tokens
    EOF         = "EOF"
    ILLEGAL     = "ILLEGAL"
    
    # Data types
    IDENT       = "IDENT"
    INT         = "INT"
    FLOAT       = "FLOAT" # as flo
    
    # Arithmetic symbols
    PLUS        = "PLUS"
    MINUS       = "MINUS"
    ASTERISK    = "ASTERISK"
    SLASH       = "SLASH"
    POW         = "POW"
    MODULUS     = "MODULUS"
    
    # Assignment Symbols
    EQ          = "EQ"
    
    # Symbols
    COLON       = "COLON"
    SEMICOLON   = "SEMICOLON"
    ARROW       = "ARROW"
    LPAREN      = "LPAREN"
    RPAREN      = "RPAREN"
    LBRACE      = "LBRACE"
    RBRACE      = "RBRACE"
    
    # Keywords
    VAR         = "VAR"
    FN          = "FN"
    RET         = "RET"
    
    # Types
    TYPE        = "TYPE"
    
class Token:
    def __init__(self, type: TokenType, literal: Any, line_no: int, position: int) -> None:
        self.type       = type
        self.literal    = literal
        self.line       = line_no
        self.position   = position
        
    def __str__(self) -> str:
        return f"Token[{self.type} : {self.literal} : Line {self.line} : Position {self.position}]"
    
    def __repr__(self) -> str:
        return f"<token {self.type} with literal {self.literal} on line {self.line}, position {self.position}>"
    
KEYWORDS: Dict[str, TokenType] = {
    "var": TokenType.VAR,
    "fn": TokenType.FN,
    "ret": TokenType.RET,
}

ALT_KEYWORDS: Dict[str, TokenType] = {
    "let": TokenType.VAR,
    "as": TokenType.COLON,
    "eq": TokenType.EQ,
    "qq": TokenType.SEMICOLON, # TODO: hey fred, are you sure this'll work?
                               # FRED: only one way to find out
                               # TODO: it's not like that
                               # FRED: if it's wrong just use an unused symbol smh
                               # TODO: whatever
    
    "pyascent_function": TokenType.FN,
    "pyascent_return": TokenType.RET,
    "returns_a": TokenType.ARROW
    
    # "SET": TokenType.VAR,
    # "AS": TokenType.COLON,
    # "BE": TokenType.EQ,
    # "END": TokenType.SEMICOLON,
    
}

TYPE_KEYWORD: List[str] = ["int", "flo"]

def lookup_ident(ident: str) -> TokenType:
    tt: TokenType | None = KEYWORDS.get(ident)
    if tt is not None:
        return tt
    
    tt = ALT_KEYWORDS.get(ident)
    if tt is not None:
        return tt

    if ident in TYPE_KEYWORD:
        return TokenType.TYPE
    
    return TokenType.IDENT