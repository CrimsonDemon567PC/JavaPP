# jppc.py
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from ast import *

# ============================================================
# Type Checker
# ============================================================

class TypeChecker:
    def __init__(self):
        self.vars = {}
        self.funcs = {}

    def infer_expr(self, node):
        if isinstance(node, IntLiteral):
            return "int"
        if isinstance(node, FloatLiteral):
            return "float"
        if isinstance(node, StringLiteral):
            return "String"
        if isinstance(node, Var):
            return self.vars.get(node.name, "var")
        if isinstance(node, ArrayAccess):
            arr_type = self.vars.get(node.array, "int[]")
            return arr_type[:-2] if arr_type.endswith("[]") else "var"
        if isinstance(node, BinOp):
            lt = self.infer_expr(node.left)
            rt = self.infer_expr(node.right)
            if "String" in (lt, rt):
                return "String"
            if "float" in (lt, rt):
                return "float"
            return "int"
        if isinstance(node, Call):
            f = self.funcs.get(node.name)
            return f["ret"] if f else "var"
        if isinstance(node, SelectExpr):
            t1 = self.infer_expr(node.if_true)
            t2 = self.infer_expr(node.if_false)
            if "String" in (t1, t2):
                return "String"
            if "float" in (t1, t2):
                return "float"
            return "int"
        if isinstance(node, FString):
            return "String"
        return "var"

    def register_var(self, name, typ):
        self.vars[name] = typ


# ============================================================
# Java Generator
# ============================================================

class JavaGen:
    def __init__(self, filename="Main"):
        self.lines = []
        self.indent = 2
        self.tc = TypeChecker()
        self.imports = set()
        self.class_name = Path(filename).stem.capitalize()

    def emit(self, line):
        self.lines.append("    " * self.indent + line)

    # ========================================================
    # Expression Generator
    # ========================================================

    def gen_expr(self, node, vector=False, arrays=None):
        arrays = arrays or set()

        if isinstance(node, IntLiteral):
            return str(node.value)

        if isinstance(node, FloatLiteral):
            return f"{node.value}f"

        if isinstance(node, StringLiteral):
            return f'"{node.value}"'

        if isinstance(node, Var):
            return f"v_{node.name}" if vector and node.name in arrays else node.name

        if isinstance(node, ArrayAccess):
            idx = self.gen_expr(node.index, vector, arrays)
            return f"{node.array}[{idx}]"

        if isinstance(node, Call):
            name = "System.out.println" if node.name == "print" else node.name
            args = ",".join(self.gen_expr(a, vector, arrays) for a in node.args)
            return f"{name}({args})"

        if isinstance(node, BinOp):
            l = self.gen_expr(node.left, vector, arrays)
            r = self.gen_expr(node.right, vector, arrays)

            if vector:
                if node.op == "+": return f"{l}.add({r})"
                if node.op == "-": return f"{l}.sub({r})"
                if node.op == "*": return f"{l}.mul({r})"
                if node.op == "/": return f"{l}.div({r})"

            if node.op == "==" and self.tc.infer_expr(node.left) == "String":
                return f"{l}.equals({r})"

            return f"({l} {node.op} {r})"

        if isinstance(node, SelectExpr):
            c = self.gen_expr(node.cond, vector, arrays)
            t = self.gen_expr(node.if_true, vector, arrays)
            f = self.gen_expr(node.if_false, vector, arrays)
            return f"({c}?{t}:{f})"

        if isinstance(node, SafeNav):
            obj = self.gen_expr(node.obj)
            return f"({obj}!=null?{obj}.{node.field}:null)"

        if isinstance(node, FString):
            parts = [
                f'"{p}"' if isinstance(p, str) else self.gen_expr(p)
                for p in node.parts
            ]
            return " + ".join(parts)

        raise RuntimeError(f"Unsupported expr: {node}")

    # ========================================================
    # Scalar Statements
    # ========================================================

    def gen_stmt_scalar(self, node):
        if isinstance(node, Assign):
            val = self.gen_expr(node.expr)
            typ = self.tc.infer_expr(node.expr)

            if isinstance(node.var, ArrayAccess):
                idx = self.gen_expr(node.var.index)
                self.emit(f"{node.var.array}[{idx}] = {val};")
            else:
                if node.var not in self.tc.vars:
                    self.emit(f"{typ} {node.var} = {val};")
                    if isinstance(node.expr, (Call, FString)):
                        pass
                    self.tc.register_var(node.var, typ)
                else:
                    self.emit(f"{node.var} = {val};")

        elif isinstance(node, IfStmt):
            self.emit(f"if({self.gen_expr(node.cond)})"+"{")
            self.indent += 1
            for s in node.body:
                self.gen_stmt_scalar(s)
            self.indent -= 1
            self.emit("}")

        elif isinstance(node, ForStmt):
            self.gen_stmt_vector(node)

        elif isinstance(node, Call):
            self.emit(self.gen_expr(node) + ";")

        elif isinstance(node, Return):
            val = self.gen_expr(node.expr) if node.expr else ""
            self.emit(f"return {val};")

    # ========================================================
    # Vectorized For Loop
    # ========================================================

    def gen_stmt_vector(self, node: ForStmt):
        arrays = {n for n, t in self.tc.vars.items() if t.endswith("[]")}

        if not arrays:
            # fallback to scalar
            start = self.gen_expr(node.start)
            end = self.gen_expr(node.end)
            self.emit(f"for(int {node.var}={start};{node.var}<{end};{node.var}++)"+"{")
            self.indent += 1
            for s in node.body:
                self.gen_stmt_scalar(s)
            self.indent -= 1
            self.emit("}")
            return

        vec = "FloatVector" if any(self.tc.vars[a] == "float[]" for a in arrays) else "IntVector"
        self.imports.add("jdk.incubator.vector.*")

        end = self.gen_expr(node.end)

        self.emit(f"var species = {vec}.SPECIES_PREFERRED;")
        self.emit(f"int bound = species.loopBound({end});")

        # vector loop
        self.emit("for(int i=0;i<bound;i+=species.length()){")
        self.indent += 1

        for a in arrays:
            self.emit(f"var v_{a} = {vec}.fromArray(species,{a},i);")

        for s in node.body:
            if isinstance(s, Assign) and isinstance(s.var, ArrayAccess):
                arr = s.var.array
                val = self.gen_expr(s.expr, True, arrays)
                self.emit(f"v_{arr} = {val};")

        for a in arrays:
            self.emit(f"v_{a}.intoArray({a},i);")

        self.indent -= 1
        self.emit("}")

        # tail loop
        self.emit(f"for(int i=bound;i<{end};i++)"+"{")
        self.indent += 1
        for s in node.body:
            self.gen_stmt_scalar(s)
        self.indent -= 1
        self.emit("}")

    # ========================================================
    # Output
    # ========================================================

    def get_output(self):
        out = []

        for imp in sorted(self.imports):
            out.append(f"import {imp};")
        if self.imports:
            out.append("")

        out.append(f"public class {self.class_name} "+"{")
        out.append("    public static void main(String[] args) {")
        out += self.lines
        out.append("    }")
        out.append("}")

        return "\n".join(out)

    def write(self, path=None):
        path = path or f"{self.class_name}.java"
        Path(path).write_text(self.get_output(), encoding="utf-8")
        print("Wrote", path)