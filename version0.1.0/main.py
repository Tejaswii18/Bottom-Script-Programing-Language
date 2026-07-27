import sys
from lexer import Lexer
from bsp_parser import Parser
from runtime import Interpreter

def run_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        interpreter = Interpreter()
        interpreter.interpret(ast)

    except FileNotFoundError:
        print(f"Error: File not found -> '{filepath}'", file=sys.stderr)
        sys.exit(64)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <script.bs>")
        sys.exit(64)
    run_file(sys.argv[1])