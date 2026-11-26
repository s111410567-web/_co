
from pathlib import Path
import sys
import re


# ==============================
# Jack Tokenizer
# ==============================

class JackTokenizer:
    def __init__(self, source):
        pattern = (
            r'"[^"\r\n]*"'
            r'|//[^\n]*'
            r'|/\*[\s\S]*?\*/'
            r'|[{}()[\].,;+\-*/&|<>=~]'
            r'|\d+'
            r'|[A-Za-z_][A-Za-z_0-9]*'
        )

        self.tokens = [
            token for token in re.findall(pattern, source)
            if not token.startswith("//")
            and not token.startswith("/*")
        ]

        self.index = 0

    def peek(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def advance(self):
        token = self.peek()
        self.index += 1
        return token

    def expect(self, expected):
        token = self.advance()

        if token != expected:
            raise SyntaxError(
                f"預期 {expected}，實際取得 {token}"
            )

        return token


# ==============================
# Symbol Table
# ==============================

class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}

        self.counts = {
            "static": 0,
            "field": 0,
            "argument": 0,
            "local": 0
        }

    def start_subroutine(self):
        self.subroutine_scope.clear()
        self.counts["argument"] = 0
        self.counts["local"] = 0

    def define(self, name, type_name, kind):
        index = self.counts[kind]

        entry = (type_name, kind, index)

        if kind in ("static", "field"):
            self.class_scope[name] = entry
        else:
            self.subroutine_scope[name] = entry

        self.counts[kind] += 1

    def var_count(self, kind):
        return self.counts[kind]

    def lookup(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]

        return self.class_scope.get(name)


# ==============================
# VM Writer
# ==============================

class VMWriter:
    def __init__(self):
        self.lines = []

    def write(self, command):
        self.lines.append(command)

    def push(self, segment, index):
        self.write(f"push {segment} {index}")

    def pop(self, segment, index):
        self.write(f"pop {segment} {index}")

    def arithmetic(self, command):
        self.write(command)

    def label(self, name):
        self.write(f"label {name}")

    def goto(self, name):
        self.write(f"goto {name}")

    def if_goto(self, name):
        self.write(f"if-goto {name}")

    def call(self, name, count):
        self.write(f"call {name} {count}")

    def function(self, name, count):
        self.write(f"function {name} {count}")

    def return_command(self):
        self.write("return")

    def save(self, path):
        path.write_text(
            "\n".join(self.lines) + "\n",
            encoding="utf-8"
        )


# ==============================
# Compilation Engine
# ==============================

class CompilationEngine:

    OPERATORS = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq"
    }

    def __init__(self, source):
        self.tokenizer = JackTokenizer(source)
        self.symbols = SymbolTable()
        self.vm = VMWriter()

        self.class_name = ""
        self.label_counter = 0

    def peek(self):
        return self.tokenizer.peek()

    def eat(self, expected=None):
        if expected is None:
            return self.tokenizer.advance()

        return self.tokenizer.expect(expected)

    def new_label(self, prefix):
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def variable(self, name):
        entry = self.symbols.lookup(name)

        if entry is None:
            raise ValueError(f"找不到變數：{name}")

        type_name, kind, index = entry

        segment = "this" if kind == "field" else kind

        return type_name, segment, index

    def push_variable(self, name):
        _, segment, index = self.variable(name)
        self.vm.push(segment, index)

    def pop_variable(self, name):
        _, segment, index = self.variable(name)
        self.vm.pop(segment, index)

    # ------------------------------
    # Class
    # ------------------------------

    def compile_class(self):
        self.eat("class")
        self.class_name = self.eat()
        self.eat("{")

        while self.peek() in ("static", "field"):
            self.compile_class_var()

        while self.peek() in (
            "constructor", "function", "method"
        ):
            self.compile_subroutine()

        self.eat("}")

    def compile_class_var(self):
        kind = self.eat()
        type_name = self.eat()

        while True:
            name = self.eat()
            self.symbols.define(name, type_name, kind)

            if self.peek() != ",":
                break

            self.eat(",")

        self.eat(";")

    # ------------------------------
    # Subroutine
    # ------------------------------

    def compile_subroutine(self):
        self.symbols.start_subroutine()

        kind = self.eat()
        self.eat()  # Return type
        name = self.eat()

        if kind == "method":
            self.symbols.define(
                "this", self.class_name, "argument"
            )

        self.eat("(")
        self.compile_parameters()
        self.eat(")")

        self.eat("{")

        while self.peek() == "var":
            self.compile_var()

        full_name = f"{self.class_name}.{name}"

        self.vm.function(
            full_name,
            self.symbols.var_count("local")
        )

        if kind == "constructor":
            self.vm.push(
                "constant",
                self.symbols.var_count("field")
            )

            self.vm.call("Memory.alloc", 1)
            self.vm.pop("pointer", 0)

        elif kind == "method":
            self.vm.push("argument", 0)
            self.vm.pop("pointer", 0)

        self.compile_statements()
        self.eat("}")

    def compile_parameters(self):
        if self.peek() == ")":
            return

        while True:
            type_name = self.eat()
            name = self.eat()

            self.symbols.define(
                name, type_name, "argument"
            )

            if self.peek() != ",":
                break

            self.eat(",")

    def compile_var(self):
        self.eat("var")
        type_name = self.eat()

        while True:
            name = self.eat()

            self.symbols.define(
                name, type_name, "local"
            )

            if self.peek() != ",":
                break

            self.eat(",")

        self.eat(";")

    # ------------------------------
    # Statements
    # ------------------------------

    def compile_statements(self):
        while True:
            token = self.peek()

            if token == "let":
                self.compile_let()

            elif token == "if":
                self.compile_if()

            elif token == "while":
                self.compile_while()

            elif token == "do":
                self.compile_do()

            elif token == "return":
                self.compile_return()

            else:
                break

    def compile_let(self):
        self.eat("let")
        name = self.eat()

        is_array = self.peek() == "["

        if is_array:
            self.push_variable(name)

            self.eat("[")
            self.compile_expression()
            self.eat("]")

            self.vm.arithmetic("add")

        self.eat("=")
        self.compile_expression()
        self.eat(";")

        if is_array:
            self.vm.pop("temp", 0)
            self.vm.pop("pointer", 1)
            self.vm.push("temp", 0)
            self.vm.pop("that", 0)

        else:
            self.pop_variable(name)

    def compile_if(self):
        self.eat("if")

        true_label = self.new_label("IF_TRUE")
        false_label = self.new_label("IF_FALSE")
        end_label = self.new_label("IF_END")

        self.eat("(")
        self.compile_expression()
        self.eat(")")

        self.vm.if_goto(true_label)
        self.vm.goto(false_label)

        self.vm.label(true_label)

        self.eat("{")
        self.compile_statements()
        self.eat("}")

        if self.peek() == "else":
            self.vm.goto(end_label)
            self.vm.label(false_label)

            self.eat("else")
            self.eat("{")
            self.compile_statements()
            self.eat("}")

            self.vm.label(end_label)

        else:
            self.vm.label(false_label)

    def compile_while(self):
        self.eat("while")

        start_label = self.new_label("WHILE_EXP")
        end_label = self.new_label("WHILE_END")

        self.vm.label(start_label)

        self.eat("(")
        self.compile_expression()
        self.eat(")")

        self.vm.arithmetic("not")
        self.vm.if_goto(end_label)

        self.eat("{")
        self.compile_statements()
        self.eat("}")

        self.vm.goto(start_label)
        self.vm.label(end_label)

    def compile_do(self):
        self.eat("do")

        name = self.eat()
        self.compile_call(name)

        self.eat(";")

        self.vm.pop("temp", 0)

    def compile_return(self):
        self.eat("return")

        if self.peek() != ";":
            self.compile_expression()

        else:
            self.vm.push("constant", 0)

        self.eat(";")
        self.vm.return_command()

    # ------------------------------
    # Expressions
    # ------------------------------

    def compile_expression(self):
        self.compile_term()

        operators = (
            "+", "-", "*", "/", "&",
            "|", "<", ">", "="
        )

        while self.peek() in operators:
            operator = self.eat()

            self.compile_term()

            if operator == "*":
                self.vm.call("Math.multiply", 2)

            elif operator == "/":
                self.vm.call("Math.divide", 2)

            else:
                self.vm.arithmetic(
                    self.OPERATORS[operator]
                )

    def compile_term(self):
        token = self.eat()

        if token is None:
            raise SyntaxError("缺少運算內容")

        # Integer constant
        if token.isdigit():
            self.vm.push("constant", int(token))

        # String constant
        elif token.startswith('"'):
            text = token[1:-1]

            self.vm.push("constant", len(text))
            self.vm.call("String.new", 1)

            for character in text:
                self.vm.push(
                    "constant", ord(character)
                )

                self.vm.call(
                    "String.appendChar", 2
                )

        # Keyword constant
        elif token in ("true", "false", "null", "this"):

            if token == "true":
                self.vm.push("constant", 0)
                self.vm.arithmetic("not")

            elif token == "this":
                self.vm.push("pointer", 0)

            else:
                self.vm.push("constant", 0)

        # Parenthesized expression
        elif token == "(":
            self.compile_expression()
            self.eat(")")

        # Unary operator
        elif token in ("-", "~"):
            self.compile_term()

            if token == "-":
                self.vm.arithmetic("neg")

            else:
                self.vm.arithmetic("not")

        # Array access
        elif self.peek() == "[":
            self.push_variable(token)

            self.eat("[")
            self.compile_expression()
            self.eat("]")

            self.vm.arithmetic("add")
            self.vm.pop("pointer", 1)
            self.vm.push("that", 0)

        # Subroutine call
        elif self.peek() in ("(", "."):
            self.compile_call(token)

        # Variable
        else:
            self.push_variable(token)

    def compile_expression_list(self):
        count = 0

        if self.peek() == ")":
            return count

        while True:
            self.compile_expression()
            count += 1

            if self.peek() != ",":
                break

            self.eat(",")

        return count

    # ------------------------------
    # Subroutine Call
    # ------------------------------

    def compile_call(self, name):
        count = 0

        if self.peek() == ".":
            self.eat(".")
            subroutine = self.eat()

            entry = self.symbols.lookup(name)

            if entry is not None:
                type_name = entry[0]

                self.push_variable(name)

                full_name = (
                    f"{type_name}.{subroutine}"
                )

                count += 1

            else:
                full_name = f"{name}.{subroutine}"

        else:
            full_name = f"{self.class_name}.{name}"

            self.vm.push("pointer", 0)
            count += 1

        self.eat("(")

        count += self.compile_expression_list()

        self.eat(")")

        self.vm.call(full_name, count)


# ==============================
# Main Program
# ==============================

def compile_file(path):
    source = path.read_text(
        encoding="utf-8-sig"
    )

    compiler = CompilationEngine(source)
    compiler.compile_class()

    output = path.with_suffix(".vm")

    compiler.vm.save(output)

    print(f"編譯完成：{output}")


def main():
    if len(sys.argv) < 2:
        print(
            "用法：python JackCompiler.py "
            "<Jack檔案或資料夾>"
        )
        return

    source = Path(sys.argv[1])

    if source.is_file() and source.suffix == ".jack":
        files = [source]

    elif source.is_dir():
        files = sorted(source.glob("*.jack"))

    else:
        print("錯誤：請指定 Jack 檔案或資料夾")
        return

    if not files:
        print("找不到 .jack 檔案")
        return

    for file in files:
        try:
            compile_file(file)

        except Exception as error:
            print(f"編譯失敗：{file}")
            print(f"錯誤原因：{error}")
            sys.exit(1)

    print("------------------------------")
    print(f"共完成 {len(files)} 個 Jack 檔案")


if __name__ == "__main__":
    main()
