from lexer import TokenType

class ASTNode:
    def __init__(self, type_, line=1, name=None):
        self.type = type_
        self.line = line
        self.name = name
        self.left = None
        self.right = None
        self.body = None
        self.else_body = None
        self.elseif_branches = [] # List of tuples: (condition, body)
        self.statements = []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        program = ASTNode("PROGRAM", 1)
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                program.statements.append(stmt)
        return program

    def _is_at_end(self):
        return self._peek().type == TokenType.EOF

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, type_):
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _match(self, *types):
        for type_ in types:
            if self._check(type_):
                self._advance()
                return True
        return False

    def _parse_expression(self):
        return self._parse_equality()

    def _parse_equality(self):
        node = self._parse_comparison()
        while self._match(TokenType.DOUBLE_EQUAL, TokenType.NOT_EQUAL):
            op = self._previous()
            parent = ASTNode("BINARY", op.line, op.lexeme)
            parent.left = node
            parent.right = self._parse_comparison()
            node = parent
        return node

    def _parse_comparison(self):
        node = self._parse_term()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op = self._previous()
            parent = ASTNode("BINARY", op.line, op.lexeme)
            parent.left = node
            parent.right = self._parse_term()
            node = parent
        return node

    def _parse_term(self):
        node = self._parse_factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            parent = ASTNode("BINARY", op.line, op.lexeme)
            parent.left = node
            parent.right = self._parse_factor()
            node = parent
        return node

    def _parse_factor(self):
        node = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous()
            parent = ASTNode("BINARY", op.line, op.lexeme)
            parent.left = node
            parent.right = self._parse_unary()
            node = parent
        return node

    def _parse_unary(self):
        if self._match(TokenType.MINUS, TokenType.PLUS):
            op = self._previous()
            node = ASTNode("UNARY", op.line, op.lexeme)
            node.left = self._parse_unary()
            return node
        return self._parse_primary()

    def _parse_primary(self):
        if self._match(TokenType.NUMBER):
            return ASTNode("LITERAL_NUMBER", self._previous().line, self._previous().lexeme)
        if self._match(TokenType.STRING):
            return ASTNode("LITERAL_STRING", self._previous().line, self._previous().lexeme)
        if self._match(TokenType.IDENTIFIER):
            return ASTNode("VARIABLE", self._previous().line, self._previous().lexeme)
        if self._match(TokenType.LEFT_PAREN):
            expr = self._parse_expression()
            self._match(TokenType.RIGHT_PAREN)
            return expr
        return None

    def _parse_block(self):
        block = ASTNode("PROGRAM", self._peek().line)
        self._match(TokenType.LEFT_BRACE)
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                block.statements.append(stmt)
        self._match(TokenType.RIGHT_BRACE)
        return block

    def _parse_show_statement(self):
        t = self._previous()
        node = ASTNode("SHOW", t.line)
        node.left = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return node

    def _parse_take_statement(self):
        t = self._previous()
        node = ASTNode("TAKE", t.line)
        if self._match(TokenType.IDENTIFIER):
            node.name = self._previous().lexeme
        self._match(TokenType.SEMICOLON)
        return node

    def _parse_let_statement(self):
        t = self._previous()
        node = ASTNode("LET", t.line)
        if self._match(TokenType.IDENTIFIER):
            node.name = self._previous().lexeme
        self._match(TokenType.EQUAL)
        node.left = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return node

    def _parse_if_statement(self):
        t = self._previous()
        node = ASTNode("IF", t.line)
        node.left = self._parse_expression() # Condition
        node.body = self._parse_block()      # True branch

        while self._match(TokenType.ELSEIF):
            ei_cond = self._parse_expression()
            ei_body = self._parse_block()
            node.elseif_branches.append((ei_cond, ei_body))

        if self._match(TokenType.ELSE):
            node.else_body = self._parse_block()
        return node

    def _parse_statement(self):
        if self._match(TokenType.SHOW): return self._parse_show_statement()
        if self._match(TokenType.TAKE): return self._parse_take_statement()
        if self._match(TokenType.LET): return self._parse_let_statement()
        if self._match(TokenType.IF): return self._parse_if_statement()

        t = self._peek()
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        stmt = ASTNode("EXPR_STMT", t.line)
        stmt.left = expr
        return stmt