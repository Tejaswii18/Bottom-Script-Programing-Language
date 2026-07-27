import enum
import string

class TokenType(enum.Enum):
    KEYWORD    = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER     = "NUMBER"
    STRING     = "STRING"
    PLUS       = "PLUS"
    MINUS      = "MINUS"
    MUL        = "MUL"
    DIV        = "DIV"
    EQ         = "EQ"
    EE         = "EE"
    NE         = "NE"
    LT         = "LT"
    LTE        = "LTE"
    GT         = "GT"
    GTE        = "GTE"
    LPAREN     = "LPAREN"
    RPAREN     = "RPAREN"
    LBRACKET   = "LBRACKET"
    RBRACKET   = "RBRACKET"
    LBRACE     = "LBRACE"
    RBRACE     = "RBRACE"
    COMMA      = "COMMA"
    COLON      = "COLON"
    DOT        = "DOT"
    PLUSEQ     = "PLUSEQ"
    ARROW      = "ARROW"
    NEWLINE    = "NEWLINE"
    EOF        = "EOF"

KEYWORDS = {
    "let", "show", "func", "return", "if", "elseif", "else", 
    "tree", "in", "range", "break", "continue", "forever", "import", "take"
}

class Token:
    def __init__(self, type_, value=None, line=0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            if self.current_char == '\n':
                self.line += 1
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\r':
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    def number(self):
        num_str = ''
        dot_count = 0
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TokenType.NUMBER, int(num_str), self.line)
        else:
            return Token(TokenType.NUMBER, float(num_str), self.line)

    def string(self):
        self.advance()
        str_val = ''
        while self.current_char is not None and self.current_char != '"':
            str_val += self.current_char
            self.advance()
        self.advance()
        return Token(TokenType.STRING, str_val, self.line)

    def identifier(self):
        id_str = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        if id_str in KEYWORDS:
            return Token(TokenType.KEYWORD, id_str, self.line)
        return Token(TokenType.IDENTIFIER, id_str, self.line)

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t\r':
                self.skip_whitespace()
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char == '\n':
                tokens.append(Token(TokenType.NEWLINE, '\n', self.line))
                self.advance()
            elif self.current_char.isdigit():
                tokens.append(self.number())
            elif self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.identifier())
            elif self.current_char == '"':
                tokens.append(self.string())
            elif self.current_char == '.':
                tokens.append(Token(TokenType.DOT, '.', self.line))
                self.advance()
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TokenType.PLUSEQ, '+=', self.line))
                else:
                    tokens.append(Token(TokenType.PLUS, '+', self.line))
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    tokens.append(Token(TokenType.ARROW, '->', self.line))
                else:
                    tokens.append(Token(TokenType.MINUS, '-', self.line))
            elif self.current_char == '*':
                self.advance()
                tokens.append(Token(TokenType.MUL, '*', self.line))
            elif self.current_char == '/':
                self.advance()
                tokens.append(Token(TokenType.DIV, '/', self.line))
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TokenType.EE, '==', self.line))
                else:
                    tokens.append(Token(TokenType.EQ, '=', self.line))
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TokenType.NE, '!=', self.line))
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TokenType.LTE, '<=', self.line))
                else:
                    tokens.append(Token(TokenType.LT, '<', self.line))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TokenType.GTE, '>=', self.line))
                else:
                    tokens.append(Token(TokenType.GT, '>', self.line))
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.line))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.line))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', self.line))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', self.line))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TokenType.LBRACE, '{', self.line))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TokenType.RBRACE, '}', self.line))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.line))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TokenType.COLON, ':', self.line))
                self.advance()
            else:
                raise SyntaxError(f"Illegal character '{self.current_char}' on line {self.line}")
        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens