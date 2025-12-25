from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler
from AST import Program
import json
import time

from llvmlite import ir # type: ignore
import llvmlite.binding as llvm # type: ignore
from ctypes import CFUNCTYPE, c_int, c_float


LEXER_DEBUG: bool = False
PARSER_DEBUG: bool = True
COMPILER_DEBUG: bool = True
RUN_CODE: bool = True

if __name__ == '__main__':
    # Read from input file
    with open("tests/test.asct", "r") as f:
        code: str = f.read()

    if LEXER_DEBUG:
        print("===== LEXER DEBUG =====")
        debug_lex: Lexer = Lexer(source=code)
        while debug_lex.current_char is not None:
            print(debug_lex.next_token())

    l: Lexer = Lexer(source=code)
    p: Parser = Parser(lexer=l)

    program: Program = p.parse_program()
    if len(p.errors) > 0:
        for err in p.errors:
            print(err)
        exit(1)

    if PARSER_DEBUG:
        print("===== PARSER DEBUG =====")
        with open("debug/ast.json", "w") as f:
            json.dump(program.json(), f, indent=4)
        print("Wrote AST to debug/ast.json successfully")

    c: Compiler = Compiler()
    c.compile(node=program)

    # Output steps
    module: ir.Module = c.module
    module.triple = llvm.get_default_triple()

    if COMPILER_DEBUG:
        with open("debug/ir.ll", "w") as f:
            f.write(str(module))
            
    if RUN_CODE:
        # llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        try:
            llvm_ir_parsed = llvm.parse_assembly(str(module))
            llvm_ir_parsed.verify()
        except Exception as e:
            print(e)
            raise
        
        target_machine = llvm.Target.from_default_triple().create_target_machine()
        
        engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
        engine.finalize_object()
        
        entry = engine.get_function_address("main")
        cfunc = CFUNCTYPE(c_int)(entry)
        
        st = time.perf_counter()
        
        result = cfunc()
        
        et = time.perf_counter()
        
        print(f"\n\n[Program returned: {result}]")
        print(f"[Executed program in {(et - st) * 1000:.6f} ms]")