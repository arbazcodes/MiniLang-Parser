import re
import sys

class MiniLangScanner:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.source_code = file.read()
        self.tokens = []
        self.keywords = {'if', 'else', 'print', 'true', 'false'}

    def scan(self):
        lines = self.source_code.split('\n')
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if line.startswith('//'):
                continue

            tokens = re.findall(r'\b(?:\d+|true|false|[a-zA-Z][a-zA-Z0-9]*|\S)\b|==|!=|[+\-*/=()]', line)
            for token in tokens:
                if token in self.keywords:
                    self.tokens.append(('KEYWORD', token))
                elif token.isdigit():
                    self.tokens.append(('INTEGER_LITERAL', int(token)))
                elif token in {'true', 'false'}:
                    self.tokens.append(('BOOLEAN_LITERAL', token == 'true'))
                elif token.isalpha():
                    self.tokens.append(('IDENTIFIER', token))
                elif token in {'+', '-', '*', '/', '=', '==', '!=', '(', ')'}:
                    self.tokens.append(('OPERATOR', token))
                else:
                    print(f"Lexical Error: Line {line_num}, unrecognized token '{token}'")

class MiniLangParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = None

    def match(self, expected_type):
        if self.current_token and self.current_token[0] == expected_type:
            self.advance()
        else:
            self.error(f"Expected {expected_type} but found {self.current_token[0] if self.current_token else 'end of input'}")

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def parse_program(self):
        # Program → Statement*
        while self.current_token:
            self.parse_statement()

    def parse_statement(self):
        # Statement → Assignment | IfStatement | PrintStatement
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.parse_assignment()
        elif self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'if':
            self.parse_if_statement()
        elif self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'print':
            self.parse_print_statement()
        elif self.current_token:
            self.error(f"Unexpected token {self.current_token[0]} in statement")

    def parse_assignment(self):
        # Assignment → IDENTIFIER '=' Expression
        identifier = self.current_token[1]
        self.match('IDENTIFIER')
        self.match('=')
        self.parse_expression()
        print(f"Assignment: {identifier}")

    def parse_if_statement(self):
        # IfStatement → 'if' Expression ':' Program ('else' ':' Program)?
        self.match('KEYWORD')
        self.parse_expression()
        self.match(':')
        self.parse_program()
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'else':
            self.match('KEYWORD')
            self.match(':')
            self.parse_program()

    def parse_print_statement(self):
        # PrintStatement → 'print' Expression
        self.match('KEYWORD')
        self.parse_expression()

    def parse_expression(self):
        # Expression → Term ( ('+' | '-') Term )*
        self.parse_term()
        while self.current_token and self.current_token[0] == 'OPERATOR' and (self.current_token[1] == '+' or self.current_token[1] == '-'):
            self.match('OPERATOR')
            self.parse_term()

    def parse_term(self):
        # Term → Factor ( ('*' | '/') Factor )*
        self.parse_factor()
        while self.current_token and self.current_token[0] == 'OPERATOR' and (self.current_token[1] == '*' or self.current_token[1] == '/'):
            self.match('OPERATOR')
            self.parse_factor()

    def parse_factor(self):
        # Factor → '(' Expression ')' | IDENTIFIER | INTEGER_LITERAL | BOOLEAN_LITERAL
        if self.current_token and self.current_token[0] == '(':
            self.match('(')
            self.parse_expression()
            self.match(')')
        elif self.current_token and (self.current_token[0] == 'IDENTIFIER' or self.current_token[0] == 'INTEGER_LITERAL' or self.current_token[0] == 'BOOLEAN_LITERAL'):
            self.match(self.current_token[0])
        elif self.current_token:
            self.error(f"Unexpected token {self.current_token[0]} in factor")

    def error(self, message):
        print(f"Syntax Error: {message}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python minilang_parser.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    scanner = MiniLangScanner(file_path)
    scanner.scan()

    print("Tokens:")
    for token_type, lexeme in scanner.tokens:
        print(f"{token_type}: {lexeme}")

    parser = MiniLangParser(scanner.tokens)
    parser.parse_program()
