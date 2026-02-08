# ast.py
# -*- coding: utf-8 -*-
"""
Java++ v4.2 AST — Production-Ready High-Performance Definitions
"""

from __future__ import annotations
from typing import List, Union, Optional


# ============================================================
# Base Node
# ============================================================

class ASTNode:
    __slots__ = ()

    def __repr__(self):
        fields = ", ".join(
            f"{k}={getattr(self, k)!r}"
            for k in getattr(self, "__slots__", ())
        )
        return f"{self.__class__.__name__}({fields})"


# ============================================================
# Program Structure
# ============================================================

class Program(ASTNode):
    __slots__ = ("stmts",)

    def __init__(self, stmts: List[ASTNode]):
        self.stmts = stmts


class ClassDef(ASTNode):
    __slots__ = ("name", "fields", "methods", "implements")

    def __init__(
        self,
        name: str,
        fields: List[str],
        methods: List["FuncDef"],
        implements: Optional[str] = None,
    ):
        self.name = name
        self.fields = fields
        self.methods = methods
        self.implements = implements


class FuncDef(ASTNode):
    __slots__ = ("name", "params", "param_types", "ret_type", "body")

    def __init__(
        self,
        name: str,
        params: List[str],
        param_types: List[str],
        ret_type: str,
        body: List[ASTNode],
    ):
        self.name = name
        self.params = params
        self.param_types = param_types
        self.ret_type = ret_type
        self.body = body


class Return(ASTNode):
    __slots__ = ("expr",)

    def __init__(self, expr: Optional[ASTNode] = None):
        self.expr = expr


# ============================================================
# Statements
# ============================================================

class Assign(ASTNode):
    __slots__ = ("var", "expr")

    def __init__(self, var: Union[str, "ArrayAccess"], expr: ASTNode):
        self.var = var
        self.expr = expr


class IfStmt(ASTNode):
    __slots__ = ("cond", "body", "orelse")

    def __init__(
        self,
        cond: ASTNode,
        body: List[ASTNode],
        orelse: Optional[List[ASTNode]] = None,
    ):
        self.cond = cond
        self.body = body
        self.orelse = orelse


class WhileStmt(ASTNode):
    __slots__ = ("cond", "body")

    def __init__(self, cond: ASTNode, body: List[ASTNode]):
        self.cond = cond
        self.body = body


class ForStmt(ASTNode):
    __slots__ = ("var", "start", "end", "body")

    def __init__(self, var: str, start: ASTNode, end: ASTNode, body: List[ASTNode]):
        self.var = var
        self.start = start
        self.end = end
        self.body = body


class Call(ASTNode):
    __slots__ = ("name", "args")

    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args


# ============================================================
# Expressions
# ============================================================

class Var(ASTNode):
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name


class ArrayAccess(ASTNode):
    __slots__ = ("array", "index")

    def __init__(self, array: str, index: ASTNode):
        self.array = array
        self.index = index


class BinOp(ASTNode):
    __slots__ = ("left", "op", "right")

    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right


class SelectExpr(ASTNode):
    __slots__ = ("cond", "if_true", "if_false")

    def __init__(self, cond: ASTNode, if_true: ASTNode, if_false: ASTNode):
        self.cond = cond
        self.if_true = if_true
        self.if_false = if_false


class SafeNav(ASTNode):
    __slots__ = ("obj", "field")

    def __init__(self, obj: ASTNode, field: str):
        self.obj = obj
        self.field = field


class FString(ASTNode):
    __slots__ = ("parts",)

    def __init__(self, parts: List[Union[str, ASTNode]]):
        self.parts = parts


# ============================================================
# Literals
# ============================================================

class IntLiteral(ASTNode):
    __slots__ = ("value",)

    def __init__(self, value: int):
        self.value = int(value)


class FloatLiteral(ASTNode):
    __slots__ = ("value",)

    def __init__(self, value: float):
        self.value = float(value)


class StringLiteral(ASTNode):
    __slots__ = ("value",)

    def __init__(self, value: str):
        self.value = value