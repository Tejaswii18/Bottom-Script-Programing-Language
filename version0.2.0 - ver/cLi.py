import sys
import os
from lexer import Lexer
from parser import Parser
from runtime import Interpreter

VERSION_INFO = """copyright © BottomScript 
2026 --version 
The net supported version--
ver--0.2.0 
bscript"""

def run_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    interpreter = Interpreter()
    try:
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        interpreter.visit(ast, interpreter.global_env)
    except Exception as e:
        print(f"RuntimeError: {e}")

def repl():
    print("BottomScript v0.2.0 REPL")
    print("Type 'exit' to quit.")
    interpreter = Interpreter()
    while True:
        try:
            text = input("bs> ")
            if text.strip() == 'exit':
                break
            if not text.strip():
                continue
            tokens = Lexer(text).tokenize()
            ast = Parser(tokens).parse()
            result = interpreter.visit(ast, interpreter.global_env)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ('--version', '--v'):
            print(VERSION_INFO)
        else:
            run_file(arg)
    else:
        repl()