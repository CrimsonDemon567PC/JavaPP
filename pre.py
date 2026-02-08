# pre.py
# -*- coding: utf-8 -*-
"""
Java++ v4.2 — Production Lexer + Recursive-Descent Parser
"""

import re
from typing import List
from ast import *

##########################
# Lexer
##########################

TOKEN_SPEC = [
    ("COMMENT",       r"\#[^\n]*"),
    ("FLOAT_LITERAL", r"\d+\.\d+"),
    ("INT_LITERAL",   r"\d+"),
    ("STRING_LITERAL", r'"(?:[^"\\]|\\.)*"'),
    ("ID",            r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",            r"\?\.|==|!=|<=|>=|[+\-*/%<>]=?|="),
    ("LBRACK",        r"\["),
    ("RBRACK",        r"\]"),
    ("LPAREN",        r"\("),
    ("RPAREN",        r"\)"),
    ("COLON",         r":"),
    ("COMMA",         r","),
    ("SEMICOLON",     r";"),
    ("NEWLINE",       r"\n"),
    ("SKIP",          r"[ \t]+"),
    ("MISMATCH",      r"."),
]

TOKEN_RE = re.compile("|".join(f"(?P<{n}>{r})" for n, r in TOKEN_SPEC))


class Token:
    __slots__ = ("type", "val")

    def __init__(self, typ: str, val: str):
        self.type = typ
        self.val = val

    def __repr__(self):
        return f"Token({self.type}, {self.val!r})"


def tokenize(code: str) -> List[Token]:
    tokens: List[Token] = []

    for m in TOKEN_RE.finditer(code):
        kind = m.lastgroup
        val = m.group()

        if kind in ("SKIP", "COMMENT"):
            continue

        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", "\n"))
            continue

        if kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character: {val}")

        tokens.append(Token(kind, val))

    tokens.append(Token("EOF", ""))
    return tokens


##########################
# Parser
##########################

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.curr = tokens[0]

    def advance(self):
        self.pos += 1
        self.curr = self.tokens[self.pos] if self.pos < len(self.tokens) else Token("EOF", "")

    def match(self, typ: str):
        if self.curr.type != typ:
            raise SyntaxError(f"Expected {typ}, got {self.curr.type}")
        val = self.curr.val
        self.advance()
        return val

    def parse_program(self):
        stmts = []

        while self.curr.type != "EOF":
            if self.curr.type == "NEWLINE":
                self.advance()
                continue

            stmt = self.parse_stmt()
            if stmt:
                stmts.append(stmt)

        return Program(stmts)

    ##########################
    # Statements
    ##########################

    def parse_stmt(self):
        if self.curr.type == "ID":

            kw = self.curr.val

            if kw == "if":
                return self.parse_if()

            if kw == "while":
                return self.parse_while()

            if kw == "for":
                return self.parse_for()

            if kw == "def":
                return self.parse_func()

            if kw == "return":
                self.advance()
                expr = None
                if self.curr.type not in ("NEWLINE", "SEMICOLON", "EOF"):
                    expr = self.parse_expr()
                self._consume_stmt_end()
                return Return(expr)

            return self.parse_assign_or_call()

        if self.curr.type == "NEWLINE":
            self.advance()
            return None

        raise SyntaxError(f"Unexpected token: {self.curr.type}")

    def _consume_stmt_end(self):
        if self.curr.type in ("NEWLINE", "SEMICOLON"):
            self.advance()

    ##########################
    # Control Flow
    ##########################

    def parse_if(self):
        self.match("ID")
        cond = self.parse_expr()
        self.match("COLON")
        body = self.parse_block()

        orelse = None
        if self.curr.type == "ID" and self.curr.val == "else":
            self.advance()
            self.match("COLON")
            orelse = self.parse_block()

        return IfStmt(cond, body, orelse)

    def parse_while(self):
        self.match("ID")
        cond = self.parse_expr()
        self.match("COLON")
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_for(self):
        self.match("ID")
        var = self.match("ID")
        self.match("COLON")
        self.match("ID")  # range
        self.match("LPAREN")
        start = self.parse_expr()
        self.match("COMMA")
        end = self.parse_expr()
        self.match("RPAREN")
        self.match("COLON")
        body = self.parse_block()
        return ForStmt(var, start, end, body)

    ##########################
    # Functions
    ##########################

    def parse_func(self):
        self.match("ID")
        name = self.match("ID")

        self.match("LPAREN")
        params = []
        param_types = []

        while self.curr.type != "RPAREN":
            pname = self.match("ID")
            ptype = "var"

            if self.curr.type == "COLON":
                self.advance()
                ptype = self.match("ID")

            params.append(pname)
            param_types.append(ptype)

            if self.curr.type == "COMMA":
                self.advance()

        self.match("RPAREN")

        ret_type = "void"
        if self.curr.type == "COLON":
            self.advance()
            ret_type = self.match("ID")

        self.match("COLON")
        body = self.parse_block()

        return FuncDef(name, params, param_types, ret_type, body)

    ##########################
    # Blocks
    ##########################

    def parse_block(self):
        stmts = []

        if self.curr.type == "NEWLINE":
            self.advance()

        while self.curr.type != "EOF":

            if self.curr.type == "NEWLINE":
                self.advance()
                continue

            if self.curr.type == "ID" and self.curr.val in ("else",):
                break

            stmt = self.parse_stmt()
            if stmt:
                stmts.append(stmt)

        return stmts

    ##########################
    # Assignments / Calls
    ##########################

    def parse_assign_or_call(self):
        name = self.match("ID")

        if self.curr.type == "LBRACK":
            self.advance()
            index = self.parse_expr()
            self.match("RBRACK")
            self.match("OP")
            expr = self.parse_expr()
            self._consume_stmt_end()
            return Assign(ArrayAccess(name, index), expr)

        if self.curr.type == "OP" and self.curr.val == "=":
            self.advance()
            expr = self.parse_expr()
            self._consume_stmt_end()
            return Assign(name, expr)

        args = []
        if self.curr.type == "LPAREN":
            self.advance()
            while self.curr.type != "RPAREN":
                args.append(self.parse_expr())
                if self.curr.type == "COMMA":
                    self.advance()
            self.match("RPAREN")

        self._consume_stmt_end()
        return Call(name, args)

    ##########################
    # Expressions
    ##########################

    def parse_expr(self):
        return self.parse_binop()

    def parse_binop(self, min_prec=0):
        left = self.parse_primary()

        while self.curr.type == "OP" and self._precedence(self.curr.val) >= min_prec:
            op = self.curr.val
            prec = self._precedence(op)
            self.advance()
            right = self.parse_binop(prec + 1)
            left = BinOp(left, op, right)

        return left

    def parse_primary(self):
        tok = self.curr

        if tok.type == "INT_LITERAL":
            self.advance()
            return IntLiteral(int(tok.val))

        if tok.type == "FLOAT_LITERAL":
            self.advance()
            return FloatLiteral(float(tok.val))

        if tok.type == "STRING_LITERAL":
            self.advance()
            return StringLiteral(tok.val[1:-1])

        if tok.type == "ID":
            self.advance()
            node = Var(tok.val)

            if self.curr.type == "OP" and self.curr.val == "?.":
                self.advance()
                fld = self.match("ID")
                return SafeNav(node, fld)

            if self.curr.type == "LBRACK":
                self.advance()
                index = self.parse_expr()
                self.match("RBRACK")
                return ArrayAccess(node.name, index)

            if self.curr.type == "LPAREN":
                self.advance()
                args = []
                while self.curr.type != "RPAREN":
                    args.append(self.parse_expr())
                    if self.curr.type == "COMMA":
                        self.advance()
                self.match("RPAREN")
                return Call(node.name, args)

            return node

        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.match("RPAREN")
            return expr

        raise SyntaxError(f"Unexpected token in expression: {tok.type}")

    ##########################
    # Precedence
    ##########################

    def _precedence(self, op: str):
        if op in ("*", "/", "%"):
            return 3
        if op in ("+", "-"):
            return 2
        if op in ("==", "!=", ">", "<", ">=", "<="):
            return 1
        if op == "=":
            return 0
        return -1