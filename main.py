# main.py
# -*- coding: utf-8 -*-

"""
Java++ Compiler Runner
End-to-End Pipeline:

.jpp source
    → Lexer (pre.py)
    → Parser → AST
    → Java Generator (jppc.py)
    → optional: javac compile

Usage:
    python main.py program.jpp
    python main.py program.jpp --run
"""

import sys
import subprocess
from pathlib import Path

from pre import tokenize, Parser
from jppc import JavaGen


# ============================================================
# Compile Pipeline
# ============================================================

def compile_jpp(source_path: Path, run: bool = False):
    if not source_path.exists():
        print(f"❌ File not found: {source_path}")
        sys.exit(1)

    code = source_path.read_text(encoding="utf-8")

    # --------------------------------------------------------
    # 1. Lexer
    # --------------------------------------------------------
    try:
        tokens = tokenize(code)
    except Exception as e:
        print("❌ Lexer error:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 2. Parser → AST
    # --------------------------------------------------------
    try:
        parser = Parser(tokens)
        program = parser.parse_program()
    except Exception as e:
        print("❌ Parser error:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 3. Java Codegen
    # --------------------------------------------------------
    try:
        gen = JavaGen(source_path.stem)
        for stmt in program.stmts:
            gen.gen_stmt_scalar(stmt)

        java_path = source_path.with_suffix(".java")
        gen.write(java_path)
    except Exception as e:
        print("❌ Code generation error:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 4. Optional: javac compile
    # --------------------------------------------------------
    if run:
        try:
            print("⚙️  Running javac...")
            subprocess.run(["javac", str(java_path)], check=True)

            class_name = java_path.stem
            print("🚀 Running Java program...\n")
            subprocess.run(["java", class_name], check=True)

        except subprocess.CalledProcessError:
            print("❌ Java compilation or execution failed.")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ javac not found. Install JDK and add to PATH.")
            sys.exit(1)


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.jpp> [--run]")
        sys.exit(0)

    source = Path(sys.argv[1])
    run_flag = "--run" in sys.argv

    compile_jpp(source, run_flag)


if __name__ == "__main__":
    main()