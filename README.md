# Java++
Python Syntax, compiles to branchless, highly optimized Java
Usage: python main.py file.jpp

---
Java++ Language Syntax Specification
- Version: 4.x
- Scope: Surface syntax only (no backend semantics)

------------------------------------------------------------
1. BASIC STRUCTURE
------------------------------------------------------------

A Java++ program consists of statements separated by:

- newline
- semicolon (;)

Example:
```
x = 5
y = 10;

print(x + y)
```
------------------------------------------------------------
2. VARIABLES AND ASSIGNMENT
------------------------------------------------------------

Assignment uses "=".
```
name = "Alice"
age = 25
pi = 3.14
```
Reassignment:
```
age = age + 1
```
------------------------------------------------------------
3. EXPRESSIONS
------------------------------------------------------------

Supported literal types:

Integers:
```
x = 5
```
Floats:
```
y = 3.14
```
Strings:
```
msg = "hello"
```
Parentheses:
```
z = (x + y) * 2
```
------------------------------------------------------------
4. OPERATORS
------------------------------------------------------------

Arithmetic:
```
a + b
a - b
a * b
a / b
```
Comparison:
```
a > b
a < b
a >= b
a <= b
a == b
a != b
```
Examples:
```
if x > 10:
    print("big")
```
------------------------------------------------------------
5. IF STATEMENTS
------------------------------------------------------------

Syntax:
```
if condition:
    block
```
Optional else:
```
if condition:
    block
else:
    block
```
Examples:
```
if x > 3:
    print("hello")

if x > 0:
    print("positive")
else:
    print("non-positive")
```
------------------------------------------------------------
6. WHILE LOOPS
------------------------------------------------------------

Syntax:
```
while condition:
    block
```
Example:
```
i = 0
while i < 5:
    print(i)
    i = i + 1
```
------------------------------------------------------------
7. FOR LOOPS (RANGE)
------------------------------------------------------------

Syntax:
```
for variable: range(start, end):
    block
```
Example:
```
for i: range(0, 5):
    print(i)
```
------------------------------------------------------------
8. FUNCTIONS
------------------------------------------------------------

Definition:
```
def name(param1, param2):
    block
```
Return value:
```
def add(a, b):
    return a + b
```
Typed parameters (optional syntax form):
```
def add(a: int, b: int):
    return a + b
```
Examples:
```
def greet(name):
    print("Hello " + name)

greet("Bob")
```
------------------------------------------------------------
9. RETURN STATEMENT
------------------------------------------------------------
```
return expression
return            # no value

Example:

def square(x):
    return x * x
```
------------------------------------------------------------
10. FUNCTION CALLS
------------------------------------------------------------
```
name(arg1, arg2)
```
Example:
```
print("hello")
result = add(2, 3)
```
------------------------------------------------------------
11. ARRAYS AND INDEXING
------------------------------------------------------------

Index access:
```
arr[i]
```
Assignment:
```
arr[i] = value
```
Example:
```
numbers[0] = 10
x = numbers[0]
```
------------------------------------------------------------
12. SELECT EXPRESSIONS (TERNARY)
------------------------------------------------------------

Syntax:
```
value_if_true if condition else value_if_false
```
Example:
```
maxVal = x if x > y else y
```
------------------------------------------------------------
13. SAFE NAVIGATION
------------------------------------------------------------

Syntax:
```
object?.field
```
Example:
```
name = user?.name
```
------------------------------------------------------------
14. F-STRINGS
------------------------------------------------------------

Syntax:
```
f"text {expression} more text"
```
Examples:
```
msg = f"Hello {name}"
info = f"x={x}, y={y}"
```
------------------------------------------------------------
15. CLASSES (BASIC FORM)
------------------------------------------------------------

Definition:
```
class Name:
    block
```
Methods inside:
```
class Person:
    def greet(self):
        print("hi")
```
------------------------------------------------------------
16. COMMENTS
------------------------------------------------------------

Single line:
```
# this is a comment
```
Example:
```
x = 5  # inline comment
```
------------------------------------------------------------
17. STATEMENT BLOCKS
------------------------------------------------------------

Blocks follow a colon (:) and are written on the next lines.

Example:
```
if x > 0:
    print("positive")
    print("still inside block")
```
------------------------------------------------------------
18. COMPLETE EXAMPLE
------------------------------------------------------------
```
# simple program

x = 5

def check(v):
    if v > 3:
        print("hello world")
    else:
        print("small")

check(x)
```
------------------------------------------------------------
END OF SYNTAX SPECIFICATION
------------------------------------------------------------
