# import sys

# class TokenType:
#     # Keywords
#     LET = "LET"
#     SHOW = "SHOW"
#     TAKE = "TAKE"
#     IF = "IF"
#     ELSE = "ELSE"
#     ELSEIF = "ELSEIF"
#     TREE = "TREE"
#     FUNC = "FUNC"
#     RETURN = "RETURN"

#     # Literals & Identifiers
#     IDENTIFIER = "IDENTIFIER"
#     STRING = "STRING"
#     NUMBER = "NUMBER"

#     # Operators & Delimiters
#     PLUS = "PLUS"
#     MINUS = "MINUS"
#     STAR = "STAR"
#     SLASH = "SLASH"
#     EQUAL = "EQUAL"
#     DOUBLE_EQUAL = "DOUBLE_EQUAL"
#     NOT_EQUAL = "NOT_EQUAL"
#     LESS = "LESS"
#     LESS_EQUAL = "LESS_EQUAL"
#     GREATER = "GREATER"
#     GREATER_EQUAL = "GREATER_EQUAL"
#     LEFT_PAREN = "LEFT_PAREN"
#     RIGHT_PAREN = "RIGHT_PAREN"
#     LEFT_BRACE = "LEFT_BRACE"
#     RIGHT_BRACE = "RIGHT_BRACE"
#     COMMA = "COMMA"
#     SEMICOLON = "SEMICOLON"
#     EOF = "EOF"
#     UNKNOWN = "UNKNOWN"

# class Token:
#     def __init__(self, type_, lexeme, line):
#         self.type = type_
#         self.lexeme = lexeme
#         self.line = line

#     def __repr__(self):
#         return f"Token({self.type}, '{self.lexeme}', line:{self.line})"

# KEYWORDS = {
#     "let": TokenType.LET,
#     "show": TokenType.SHOW,
#     "take": TokenType.TAKE,
#     "if": TokenType.IF,
#     "else": TokenType.ELSE,
#     "elseif": TokenType.ELSEIF,
#     "tree": TokenType.TREE,
#     "func": TokenType.FUNC,
#     "return": TokenType.RETURN,
# }

# class Lexer:
#     def __init__(self, source):
#         self.source = source
#         self.start = 0
#         self.current = 0
#         self.line = 1
#         self.tokens = []

#     def tokenize(self):
#         while not self._is_at_end():
#             self.start = self.current
#             self._scan_token()
#         self.tokens.append(Token(TokenType.EOF, "", self.line))
#         return self.tokens

#     def _is_at_end(self):
#         return self.current >= len(self.source)

#     def _advance(self):
#         c = self.source[self.current]
#         self.current += 1
#         return c

#     def _peek(self):
#         if self._is_at_end():
#             return '\0'
#         return self.source[self.current]

#     def _peek_next(self):
#         if self.current + 1 >= len(self.source):
#             return '\0'
#         return self.source[self.current + 1]

#     def _match(self, expected):
#         if self._is_at_end() or self.source[self.current] != expected:
#             return False
#         self.current += 1
#         return True

#     def _scan_token(self):
#         c = self._advance()
#         if c in (' ', '\r', '\t'):
#             return
#         if c == '\n':
#             self.line += 1
#             return
        
#         # Single-character tokens
#         if c == '(': self.tokens.append(Token(TokenType.LEFT_PAREN, '(', self.line))
#         elif c == ')': self.tokens.append(Token(TokenType.RIGHT_PAREN, ')', self.line))
#         elif c == '{': self.tokens.append(Token(TokenType.LEFT_BRACE, '{', self.line))
#         elif c == '}': self.tokens.append(Token(TokenType.RIGHT_BRACE, '}', self.line))
#         elif c == ',': self.tokens.append(Token(TokenType.COMMA, ',', self.line))
#         elif c == ';': self.tokens.append(Token(TokenType.SEMICOLON, ';', self.line))
#         elif c == '+': self.tokens.append(Token(TokenType.PLUS, '+', self.line))
#         elif c == '-': self.tokens.append(Token(TokenType.MINUS, '-', self.line))
#         elif c == '*': self.tokens.append(Token(TokenType.STAR, '*', self.line))
#         elif c == '/': self.tokens.append(Token(TokenType.SLASH, '/', self.line))
        
#         # Operators
#         elif c == '=':
#             type_ = TokenType.DOUBLE_EQUAL if self._match('=') else TokenType.EQUAL
#             self.tokens.append(Token(type_, '==' if type_ == TokenType.DOUBLE_EQUAL else '=', self.line))
#         elif c == '!':
#             if self._match('='):
#                 self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line))
#             else:
#                 self.tokens.append(Token(TokenType.UNKNOWN, '!', self.line))
#         elif c == '<':
#             type_ = TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS
#             self.tokens.append(Token(type_, '<=' if type_ == TokenType.LESS_EQUAL else '<', self.line))
#         elif c == '>':
#             type_ = TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER
#             self.tokens.append(Token(type_, '>=' if type_ == TokenType.GREATER_EQUAL else '>', self.line))
        
#         # Strings
#         elif c == '"':
#             while self._peek() != '"' and not self._is_at_end():
#                 if self._peek() == '\n':
#                     self.line += 1
#                 self._advance()
#             if self._is_at_end():
#                 print(f"Lexical Error: Unterminated string at line {self.line}", file=sys.stderr)
#                 return
#             self._advance() # Closing quote
#             value = self.source[self.start + 1 : self.current - 1]
#             self.tokens.append(Token(TokenType.STRING, value, self.line))
        
#         # Numbers & Identifiers
#         else:
#             if self._is_digit(c):
#                 while self._is_digit(self._peek()):
#                     self._advance()
#                 if self._peek() == '.' and self._is_digit(self._peek_next()):
#                     self._advance() # Consume '.'
#                     while self._is_digit(self._peek()):
#                         self._advance()
#                 value = self.source[self.start:self.current]
#                 self.tokens.append(Token(TokenType.NUMBER, value, self.line))
#             elif self._is_alpha(c):
#                 while self._is_alnum(self._peek()):
#                     self._advance()
#                 text = self.source[self.start:self.current]
#                 type_ = KEYWORDS.get(text, TokenType.IDENTIFIER)
#                 self.tokens.append(Token(type_, text, self.line))
#             else:
#                 print(f"Lexical Error: Unexpected character '{c}' at line {self.line}", file=sys.stderr)

#     def _is_digit(self, c):
#         return '0' <= c <= '9'

#     def _is_alpha(self, c):
#         return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'

#     def _is_alnum(self, c):
#         return self._is_alpha(c) or self._is_digit(c)








import sys

class TokenType:
    # Keywords
    LET = "LET"
    SHOW = "SHOW"
    TAKE = "TAKE"
    IF = "IF"
    ELSE = "ELSE"
    ELSEIF = "ELSEIF"
    TREE = "TREE"
    FUNC = "FUNC"
    RETURN = "RETURN"

    # Literals & Identifiers
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # Operators & Delimiters
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    EQUAL = "EQUAL"
    DOUBLE_EQUAL = "DOUBLE_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

class Token:
    def __init__(self, type_, lexeme, line):
        self.type = type_
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', line:{self.line})"

KEYWORDS = {
    "let": TokenType.LET,
    "show": TokenType.SHOW,
    "take": TokenType.TAKE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elseif": TokenType.ELSEIF,
    "tree": TokenType.TREE,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
}

class Lexer:
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

    def tokenize(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _match(self, expected):
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _scan_token(self):
        c = self._advance()
        if c in (' ', '\r', '\t'):
            return
        if c == '\n':
            self.line += 1
            return
        
        # Single-character tokens
        if c == '(': self.tokens.append(Token(TokenType.LEFT_PAREN, '(', self.line))
        elif c == ')': self.tokens.append(Token(TokenType.RIGHT_PAREN, ')', self.line))
        elif c == '{': self.tokens.append(Token(TokenType.LEFT_BRACE, '{', self.line))
        elif c == '}': self.tokens.append(Token(TokenType.RIGHT_BRACE, '}', self.line))
        elif c == ',': self.tokens.append(Token(TokenType.COMMA, ',', self.line))
        elif c == ';': self.tokens.append(Token(TokenType.SEMICOLON, ';', self.line))
        elif c == '+': self.tokens.append(Token(TokenType.PLUS, '+', self.line))
        elif c == '-': self.tokens.append(Token(TokenType.MINUS, '-', self.line))
        elif c == '*': self.tokens.append(Token(TokenType.STAR, '*', self.line))
        
        elif c == '/':
            if self._match('/'):
                # A comment goes until the end of the line.
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self.tokens.append(Token(TokenType.SLASH, '/', self.line))
        
        # Operators
        elif c == '=':
            type_ = TokenType.DOUBLE_EQUAL if self._match('=') else TokenType.EQUAL
            self.tokens.append(Token(type_, '==' if type_ == TokenType.DOUBLE_EQUAL else '=', self.line))
        elif c == '!':
            if self._match('='):
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line))
            else:
                self.tokens.append(Token(TokenType.UNKNOWN, '!', self.line))
        elif c == '<':
            type_ = TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS
            self.tokens.append(Token(type_, '<=' if type_ == TokenType.LESS_EQUAL else '<', self.line))
        elif c == '>':
            type_ = TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER
            self.tokens.append(Token(type_, '>=' if type_ == TokenType.GREATER_EQUAL else '>', self.line))
        
        # Strings
        elif c == '"':
            while self._peek() != '"' and not self._is_at_end():
                if self._peek() == '\n':
                    self.line += 1
                self._advance()
            if self._is_at_end():
                print(f"Lexical Error: Unterminated string at line {self.line}", file=sys.stderr)
                return
            self._advance() # Closing quote
            value = self.source[self.start + 1 : self.current - 1]
            self.tokens.append(Token(TokenType.STRING, value, self.line))
        
        # Numbers & Identifiers
        else:
            if self._is_digit(c):
                while self._is_digit(self._peek()):
                    self._advance()
                if self._peek() == '.' and self._is_digit(self._peek_next()):
                    self._advance() # Consume '.'
                    while self._is_digit(self._peek()):
                        self._advance()
                value = self.source[self.start:self.current]
                self.tokens.append(Token(TokenType.NUMBER, value, self.line))
            elif self._is_alpha(c):
                while self._is_alnum(self._peek()):
                    self._advance()
                text = self.source[self.start:self.current]
                type_ = KEYWORDS.get(text, TokenType.IDENTIFIER)
                self.tokens.append(Token(type_, text, self.line))
            else:
                print(f"Lexical Error: Unexpected character '{c}' at line {self.line}", file=sys.stderr)

    def _is_digit(self, c):
        return '0' <= c <= '9'

    def _is_alpha(self, c):
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'

    def _is_alnum(self, c):
        return self._is_alpha(c) or self._is_digit(c)