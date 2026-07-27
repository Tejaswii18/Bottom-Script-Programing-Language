import math
import os

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.constants = set()
        self.parent = parent

    def get(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'")

    def set(self, name, value, is_const=False):
        if name in self.constants:
            raise PermissionError(f"Cannot modify immutable constant '{name}'")
        self.symbols[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name, value):
        if name in self.constants:
            raise PermissionError(f"Cannot reassign constant '{name}'")
        if name in self.symbols:
            self.symbols[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'")

class Function:
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env

    def execute(self, args, interpreter):
        local_env = SymbolTable(self.env)
        for p, a in zip(self.params, args):
            local_env.set(p, a)
        try:
            for stmt in self.body:
                interpreter.visit(stmt, local_env)
        except ReturnSignal as ret:
            return ret.value
        return None

class Interpreter:
    def __init__(self):
        self.global_env = SymbolTable()
        self.setup_builtins()

    def setup_builtins(self):
        math_module = {
            "sqrt": lambda x: math.sqrt(x),
            "sin": lambda x: math.sin(x),
            "cos": lambda x: math.cos(x),
            "tan": lambda x: math.tan(x),
            "min": lambda *args: min(*args),  
            "max": lambda *args: max(*args),
            "pi": math.pi,
            "e": math.e
        }
        self.global_env.set("math", math_module)
        
        # Enhanced Built-ins
        self.global_env.set("take", lambda prompt="": input(prompt))
        self.global_env.set("len", lambda obj: len(obj))
        self.global_env.set("type", lambda obj: type(obj).__name__)
        self.global_env.set("int", lambda x: int(x))
        self.global_env.set("float", lambda x: float(x))
        self.global_env.set("str", lambda x: str(x))

        # File I/O Helpers
        def read_file(filepath):
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            raise FileNotFoundError(f"File not found: {filepath}")

        def write_file(filepath, content):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return True

        self.global_env.set("readFile", read_file)
        self.global_env.set("writeFile", write_file)

    def visit(self, node, env):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.no_visit_method)
        return visitor(node, env)

    def no_visit_method(self, node, env):
        raise NotImplementedError(f'visit_{type(node).__name__} not defined')

    def visit_ProgramNode(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
        return result

    def visit_VarDeclNode(self, node, env):
        val = self.visit(node.value, env)
        env.set(node.name, val, node.is_const)
        return val

    def visit_AssignNode(self, node, env):
        val = self.visit(node.value, env)
        env.assign(node.name, val)
        return val

    def visit_AugmentedAssignNode(self, node, env):
        current = env.get(node.name)
        val = self.visit(node.value, env)
        if node.op == '+=':
            if isinstance(current, str) or isinstance(val, str):
                new_val = str(current) + str(val)
            else:
                new_val = current + val
        else:
            raise SyntaxError(f"Unsupported operator {node.op}")
        env.assign(node.name, new_val)
        return new_val

    def visit_ShowNode(self, node, env):
        val = self.visit(node.expr, env)
        print(val)
        return val

    def visit_FuncDefNode(self, node, env):
        func = Function(node.name, node.params, node.body, env)
        env.set(node.name, func)
        return func

    def visit_ReturnNode(self, node, env):
        val = self.visit(node.expr, env) if node.expr else None
        raise ReturnSignal(val)

    def visit_IfNode(self, node, env):
        for cond, body in node.cases:
            if self.visit(cond, env):
                res = None
                for stmt in body:
                    res = self.visit(stmt, env)
                return res
        if node.else_case:
            res = None
            for stmt in node.else_case:
                res = self.visit(stmt, env)
            return res
        return None

    def visit_TreeLoopNode(self, node, env):
        if node.loop_type == 'range':
            start = self.visit(node.iterable_or_condition[0], env)
            end = self.visit(node.iterable_or_condition[1], env)
            for i in range(start, end):
                env.set(node.target, i)
                try:
                    for stmt in node.body:
                        self.visit(stmt, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        elif node.loop_type == 'array':
            iterable = self.visit(node.iterable_or_condition, env)
            for item in iterable:
                env.set(node.target, item)
                try:
                    for stmt in node.body:
                        self.visit(stmt, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        elif node.loop_type == 'dict':
            iterable = self.visit(node.iterable_or_condition, env)
            t1, t2 = node.target
            for k, v in iterable.items():
                env.set(t1, k)
                env.set(t2, v)
                try:
                    for stmt in node.body:
                        self.visit(stmt, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        elif node.loop_type == 'while':
            while self.visit(node.iterable_or_condition, env):
                try:
                    for stmt in node.body:
                        self.visit(stmt, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        elif node.loop_type == 'forever':
            while True:
                try:
                    for stmt in node.body:
                        self.visit(stmt, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        return None

    def visit_BreakNode(self, node, env):
        raise BreakSignal()

    def visit_ContinueNode(self, node, env):
        raise ContinueSignal()

    def visit_ImportNode(self, node, env):
        mod_name = node.module_name
        if mod_name == 'math':
            return env.get('math')
        elif isinstance(mod_name, str) and mod_name.endswith('.bs'):
            if os.path.exists(mod_name):
                with open(mod_name, 'r', encoding='utf-8') as f:
                    code = f.read()
                from lexer import Lexer
                from parser import Parser
                tokens = Lexer(code).tokenize()
                ast = Parser(tokens).parse()
                return self.visit(ast, env)
        raise FileNotFoundError(f"Module '{mod_name}' not found.")

    def visit_BinOpNode(self, node, env):
        left = self.visit(node.left, env)
        right = self.visit(node.right, env)
        op = node.op.type

        try:
            if op.name == 'PLUS':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op.name == 'MINUS':
                return left - right
            elif op.name == 'MUL':
                return left * right
            elif op.name == 'DIV':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            elif op.name == 'EE':
                return left == right
            elif op.name == 'NE':
                return left != right
            elif op.name == 'LT':
                return left < right
            elif op.name == 'LTE':
                return left <= right
            elif op.name == 'GT':
                return left > right
            elif op.name == 'GTE':
                return left >= right
        except TypeError:
            raise TypeError(f"Unsupported operation between {type(left).__name__} and {type(right).__name__}")

    def visit_NumNode(self, node, env):
        return node.value

    def visit_StringNode(self, node, env):
        return node.value

    def visit_VarAccessNode(self, node, env):
        return env.get(node.name)

    def visit_MemberAccessNode(self, node, env):
        obj = self.visit(node.obj, env)
        if isinstance(obj, dict):
            if node.member in obj:
                return obj[node.member]
            raise AttributeError(f"Module or object has no member '{node.member}'")
        raise TypeError("Member access not supported on this type")

    def visit_ArrayNode(self, node, env):
        return [self.visit(el, env) for el in node.elements]

    def visit_DictNode(self, node, env):
        return {self.visit(k, env): self.visit(v, env) for k, v in node.pairs}

    def visit_CallNode(self, node, env):
        callable_obj = self.visit(node.node_to_call, env)
        args = [self.visit(arg, env) for arg in node.args]
        if isinstance(callable_obj, Function):
            return callable_obj.execute(args, self)
        elif callable(callable_obj):
            return callable_obj(*args)
        raise TypeError("Object is not callable")