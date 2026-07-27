from lexer import TokenType

class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDeclNode(ASTNode):
    def __init__(self, name, value, is_const=False):
        self.name = name
        self.value = value
        self.is_const = is_const

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class AugmentedAssignNode(ASTNode):
    def __init__(self, name, op, value):
        self.name = name
        self.op = op
        self.value = value

class ShowNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class FuncDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class IfNode(ASTNode):
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

class TreeLoopNode(ASTNode):
    def __init__(self, loop_type, target, iterable_or_condition, body):
        self.loop_type = loop_type
        self.target = target        
        self.iterable_or_condition = iterable_or_condition
        self.body = body

class BreakNode(ASTNode):
    pass

class ContinueNode(ASTNode):
    pass

class ImportNode(ASTNode):
    def __init__(self, module_name):
        self.module_name = module_name

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class NumNode(ASTNode):
    def __init__(self, tok):
        self.tok = tok
        self.value = tok.value

class StringNode(ASTNode):
    def __init__(self, tok):
        self.tok = tok
        self.value = tok.value

class VarAccessNode(ASTNode):
    def __init__(self, tok):
        self.tok = tok
        self.name = tok.value

class MemberAccessNode(ASTNode):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

class ArrayNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class DictNode(ASTNode):
    def __init__(self, pairs):
        self.pairs = pairs

class CallNode(ASTNode):
    def __init__(self, node_to_call, args):
        self.node_to_call = node_to_call
        self.args = args

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def parse(self):
        statements = []
        self.skip_newlines()
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        return ProgramNode(statements)

    def statement(self):
        self.skip_newlines()
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None

        if self.current_token.type == TokenType.KEYWORD:
            val = self.current_token.value
            if val == 'let':
                return self.var_decl()
            elif val == 'show':
                return self.show_stmt()
            elif val == 'func':
                return self.func_def()
            elif val == 'return':
                return self.return_stmt()
            elif val == 'if':
                return self.if_stmt()
            elif val == 'tree':
                return self.tree_loop()
            elif val == 'break':
                self.advance()
                return BreakNode()
            elif val == 'continue':
                self.advance()
                return ContinueNode()
            elif val == 'import':
                return self.import_stmt()

        if self.current_token.type == TokenType.IDENTIFIER or (self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'take'):
            tok = self.current_token
            self.advance()
            if self.current_token and self.current_token.type == TokenType.EQ:
                self.advance()
                expr = self.expr()
                return AssignNode(tok.value, expr)
            elif self.current_token and self.current_token.type == TokenType.PLUSEQ:
                op = self.current_token.value
                self.advance()
                expr = self.expr()
                return AugmentedAssignNode(tok.value, op, expr)
            else:
                self.pos -= 1
                self.current_token = self.tokens[self.pos]

        return self.expr()

    def import_stmt(self):
        self.advance()
        if self.current_token.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.KEYWORD):
            mod = self.current_token.value
            self.advance()
            return ImportNode(mod)
        raise SyntaxError("Expected module name after import")

    def var_decl(self):
        self.advance()
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Expected variable name after 'let'")
        name = self.current_token.value
        self.advance()

        if self.current_token.type != TokenType.EQ:
            raise SyntaxError("Expected '=' in variable declaration")
        self.advance()

        is_const = False
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                is_const = True
                self.advance()
                val_expr = self.expr()
                if self.current_token and self.current_token.type == TokenType.RPAREN:
                    self.advance()
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                return VarDeclNode(name, val_expr, is_const=True)
            else:
                self.pos -= 2
                self.current_token = self.tokens[self.pos]

        expr = self.expr()
        return VarDeclNode(name, expr, is_const=False)

    def show_stmt(self):
        self.advance()
        expr = self.expr()
        return ShowNode(expr)

    def func_def(self):
        self.advance()
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Expected function name")
        name = self.current_token.value
        self.advance()

        if self.current_token.type != TokenType.LPAREN:
            raise SyntaxError("Expected '(' after function name")
        self.advance()

        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.current_token.value)
            self.advance()
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                params.append(self.current_token.value)
                self.advance()

        if self.current_token.type != TokenType.RPAREN:
            raise SyntaxError("Expected ')' after parameters")
        self.advance()

        body = self.parse_block_or_braces()
        return FuncDefNode(name, params, body)

    def return_stmt(self):
        self.advance()
        if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
            expr = self.expr()
            return ReturnNode(expr)
        return ReturnNode(None)

    def parse_block_or_braces(self):
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
            return self.parse_block()
        elif self.current_token and self.current_token.type == TokenType.LBRACE:
            return self.parse_brace_block()
        else:
            raise SyntaxError("Expected ':' or '{' for block")

    def parse_brace_block(self):
        self.advance()
        statements = []
        self.skip_newlines()
        while self.current_token and self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        if self.current_token and self.current_token.type == TokenType.RBRACE:
            self.advance()
        else:
            raise SyntaxError("Expected '}' to close block")
        return statements

    def parse_block(self):
        statements = []
        self.skip_newlines()
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            return self.parse_brace_block()
        while self.current_token and self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            break
        return statements

    def if_stmt(self):
        cases = []
        else_case = None
        self.advance()
        
        has_paren = False
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            has_paren = True
            self.advance()
            
        condition = self.expr()
        
        if has_paren and self.current_token and self.current_token.type == TokenType.RPAREN:
            self.advance()

        body = self.parse_block_or_braces()
        cases.append((condition, body))

        while self.current_token:
            self.skip_newlines()
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'elseif':
                self.advance()
                has_p = False
                if self.current_token and self.current_token.type == TokenType.LPAREN:
                    has_p = True
                    self.advance()
                cond = self.expr()
                if has_p and self.current_token and self.current_token.type == TokenType.RPAREN:
                    self.advance()
                b = self.parse_block_or_braces()
                cases.append((cond, b))
            elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'else':
                self.advance()
                self.skip_newlines()
                if self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'if':
                    self.advance()
                    has_p = False
                    if self.current_token and self.current_token.type == TokenType.LPAREN:
                        has_p = True
                        self.advance()
                    cond = self.expr()
                    if has_p and self.current_token and self.current_token.type == TokenType.RPAREN:
                        self.advance()
                    b = self.parse_block_or_braces()
                    cases.append((cond, b))
                else:
                    else_case = self.parse_block_or_braces()
                    break
            else:
                break

        return IfNode(cases, else_case)

    def tree_loop(self):
        self.advance()
        if self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'forever':
            self.advance()
            body = self.parse_block_or_braces()
            return TreeLoopNode('forever', None, None, body)

        saved_pos = self.pos
        target_name = self.current_token.value
        self.advance()
        
        second_target = None
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
            second_target = self.current_token.value
            self.advance()

        is_in_loop = self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'in'
        self.pos = saved_pos
        self.current_token = self.tokens[self.pos]

        if is_in_loop:
            if second_target:
                t1 = self.current_token.value
                self.advance()
                self.advance()
                t2 = self.current_token.value
                self.advance()
                self.advance()
                iterable = self.expr()
                body = self.parse_block_or_braces()
                return TreeLoopNode('dict', (t1, t2), iterable, body)
            else:
                t1 = self.current_token.value
                self.advance()
                self.advance()
                if self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'range':
                    self.advance()
                    if self.current_token.type != TokenType.LPAREN:
                        raise SyntaxError("Expected '(' after range")
                    self.advance()
                    start = self.expr()
                    if self.current_token.type != TokenType.COMMA:
                        raise SyntaxError("Expected ',' in range")
                    self.advance()
                    end = self.expr()
                    if self.current_token.type != TokenType.RPAREN:
                        raise SyntaxError("Expected ')' after range")
                    self.advance()
                    body = self.parse_block_or_braces()
                    return TreeLoopNode('range', t1, (start, end), body)
                else:
                    iterable = self.expr()
                    body = self.parse_block_or_braces()
                    return TreeLoopNode('array', t1, iterable, body)
        else:
            has_paren = False
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                has_paren = True
                self.advance()
            condition = self.expr()
            if has_paren and self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
            body = self.parse_block_or_braces()
            return TreeLoopNode('while', None, condition, body)

    def expr(self):
        return self.comparison()

    def comparison(self):
        node = self.arithmetic()
        while self.current_token and self.current_token.type in (TokenType.EE, TokenType.NE, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op_tok = self.current_token
            self.advance()
            node = BinOpNode(node, op_tok, self.arithmetic())
        return node

    def arithmetic(self):
        node = self.term()
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self.current_token
            self.advance()
            node = BinOpNode(node, op_tok, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op_tok = self.current_token
            self.advance()
            node = BinOpNode(node, op_tok, self.factor())
        return node

    def factor(self):
        tok = self.current_token
        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumNode(tok)
        elif tok.type == TokenType.STRING:
            self.advance()
            return StringNode(tok)
        elif tok.type == TokenType.IDENTIFIER or (tok.type == TokenType.KEYWORD and tok.value == 'take'):
            self.advance()
            node = VarAccessNode(tok)
            return self.trailer(node)
        elif tok.type == TokenType.LPAREN:
            self.advance()
            node = self.expr()
            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Expected ')'")
            self.advance()
            return self.trailer(node)
        elif tok.type == TokenType.LBRACKET:
            return self.array_literal()
        elif tok.type == TokenType.LBRACE:
            return self.dict_literal()
        raise SyntaxError(f"Unexpected token '{tok.value}'")

    def trailer(self, node):
        while self.current_token:
            if self.current_token.type == TokenType.LPAREN:
                self.advance()
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expr())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        args.append(self.expr())
                if self.current_token.type != TokenType.RPAREN:
                    raise SyntaxError("Expected ')' after arguments")
                self.advance()
                node = CallNode(node, args)
            elif self.current_token.type == TokenType.DOT:
                self.advance()
                if self.current_token.type != TokenType.IDENTIFIER:
                    raise SyntaxError("Expected identifier after '.'")
                member = self.current_token.value
                self.advance()
                node = MemberAccessNode(node, member)
            else:
                break
        return node

    def array_literal(self):
        self.advance()
        elements = []
        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                elements.append(self.expr())
        if self.current_token.type != TokenType.RBRACKET:
            raise SyntaxError("Expected ']'")
        self.advance()
        return ArrayNode(elements)

    def dict_literal(self):
        self.advance()
        pairs = []
        if self.current_token.type != TokenType.RBRACE:
            key = self.expr()
            if self.current_token.type != TokenType.COLON:
                raise SyntaxError("Expected ':' in dictionary pair")
            self.advance()
            val = self.expr()
            pairs.append((key, val))
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                key = self.expr()
                if self.current_token.type != TokenType.COLON:
                    raise SyntaxError("Expected ':' in dictionary pair")
                self.advance()
                val = self.expr()
                pairs.append((key, val))
        if self.current_token.type != TokenType.RBRACE:
            raise SyntaxError("Expected '}'")
        self.advance()
        return DictNode(pairs)