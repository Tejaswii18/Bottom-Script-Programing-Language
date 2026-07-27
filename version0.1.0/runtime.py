import sys

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'.")

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name)
        return None

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.env = self.globals

    def interpret(self, ast):
        try:
            self._execute(ast)
        except Exception as e:
            print(f"Runtime Error: {e}", file=sys.stderr)

    def _execute(self, node):
        if not node:
            return

        if node.type == "PROGRAM":
            previous_env = self.env
            self.env = Environment(previous_env)
            try:
                for stmt in node.statements:
                    self._execute(stmt)
            finally:
                self.env = previous_env

        elif node.type == "SHOW":
            val = self._evaluate(node.left)
            print("" if val is None else val)

        elif node.type == "TAKE":
            user_input = input()
            self.env.define(node.name, user_input)

        elif node.type == "LET":
            val = self._evaluate(node.left)
            self.env.define(node.name, val)

        elif node.type == "IF":
            cond = self._evaluate(node.left)
            if self._is_truthy(cond):
                self._execute(node.body)
            else:
                executed = False
                for ei_cond_node, ei_body in node.elseif_branches:
                    ei_cond = self._evaluate(ei_cond_node)
                    if self._is_truthy(ei_cond):
                        self._execute(ei_body)
                        executed = True
                        break
                if not executed and node.else_body:
                    self._execute(node.else_body)

        elif node.type == "EXPR_STMT":
            self._evaluate(node.left)

    def _evaluate(self, node):
        if not node:
            return None

        if node.type == "LITERAL_NUMBER":
            return float(node.name) if '.' in node.name else int(node.name)
        
        elif node.type == "LITERAL_STRING":
            return node.name

        elif node.type == "VARIABLE":
            val = self.env.get(node.name)
            if val is not None:
                return val
            raise RuntimeError(f"Undefined variable '{node.name}' at line {node.line}")

        elif node.type == "BINARY":
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if left is None or right is None:
                raise RuntimeError(f"Invalid operands (NoneType) in binary operation '{node.name}' at line {node.line}")

            if node.name == "+":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                return str(left) + str(right)
            elif node.name == "-":
                return left - right
            elif node.name == "*":
                return left * right
            elif node.name == "/":
                if right == 0:
                    raise RuntimeError(f"Division by zero at line {node.line}")
                return left / right
            elif node.name == "==":
                return 1 if left == right else 0
            elif node.name == "!=":
                return 1 if left != right else 0
            elif node.name == "<":
                return 1 if left < right else 0
            elif node.name == "<=":
                return 1 if left <= right else 0
            elif node.name == ">":
                return 1 if left > right else 0
            elif node.name == ">=":
                return 1 if left >= right else 0

        return None

    def _is_truthy(self, val):
        if val is None:
            return False
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return len(val) > 0
        return bool(val)