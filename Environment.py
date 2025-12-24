from typing import Dict, Optional, Tuple
from llvmlite import ir # type: ignore


class Environment:
    def __init__(self, records: Optional[Dict[str, Tuple[ir.Value, ir.Type]]] = None, 
                 parent = None, name: str = "global") -> None:
        self.records = records if records else {}
        self.parent = parent
        self.name = name
    
    def define(self, name: str, value: ir.Value, _type: ir.Type) -> ir.Value:
        self.records[name] = (value, _type)
        return value
    
    def lookup(self, name: str) -> Tuple[ir.Value, ir.Type]:
        return self.__resolve(name)
    
    def __resolve(self, name: str) -> Tuple[ir.Value, ir.Type]:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.__resolve(name)
        else:
            return None # type: ignore
