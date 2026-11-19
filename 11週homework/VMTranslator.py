from pathlib import Path
import sys


class VMTranslator:
    def __init__(self):
        self.lines = []
        self.counter = 0
        self.current_file = ""
        self.current_function = ""

    def emit(self, *lines):
        self.lines.extend(lines)

    def unique(self, prefix):
        self.counter += 1
        return f"{prefix}.{self.counter}"

    def push_d(self):
        self.emit(
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        )

    def pop_d(self):
        self.emit("@SP", "AM=M-1", "D=M")

    def arithmetic(self, command):
        if command in ("neg", "not"):
            self.emit("@SP", "A=M-1",
                      "M=-M" if command == "neg" else "M=!M")
            return

        if command in ("add", "sub", "and", "or"):
            operations = {
                "add": "M=D+M",
                "sub": "M=M-D",
                "and": "M=D&M",
                "or": "M=D|M",
            }
            self.emit("@SP", "AM=M-1", "D=M",
                      "A=A-1", operations[command])
            return

        if command in ("eq", "gt", "lt"):
            true_label = self.unique("TRUE")
            end_label = self.unique("END")
            jump = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]

            self.emit(
                "@SP", "AM=M-1", "D=M",
                "A=A-1", "D=M-D",
                f"@{true_label}", f"D;{jump}",
                "@SP", "A=M-1", "M=0",
                f"@{end_label}", "0;JMP",
                f"({true_label})",
                "@SP", "A=M-1", "M=-1",
                f"({end_label})"
            )
            return

        raise ValueError(f"不支援的運算：{command}")

    def push(self, segment, index):
        if segment == "constant":
            self.emit(f"@{index}", "D=A")
        elif segment in ("local", "argument", "this", "that"):
            base = {
                "local": "LCL", "argument": "ARG",
                "this": "THIS", "that": "THAT"
            }[segment]
            self.emit(f"@{base}", "D=M",
                      f"@{index}", "A=D+A", "D=M")
        elif segment == "temp":
            self.emit(f"@{5 + index}", "D=M")
        elif segment == "pointer":
            self.emit(f"@{3 + index}", "D=M")
        elif segment == "static":
            self.emit(f"@{self.current_file}.{index}", "D=M")
        else:
            raise ValueError(f"不支援的 segment：{segment}")

        self.push_d()

    def pop(self, segment, index):
        if segment in ("local", "argument", "this", "that"):
            base = {
                "local": "LCL", "argument": "ARG",
                "this": "THIS", "that": "THAT"
            }[segment]
            self.emit(
                f"@{base}", "D=M",
                f"@{index}", "D=D+A",
                "@R13", "M=D"
            )
            self.pop_d()
            self.emit("@R13", "A=M", "M=D")
        elif segment == "temp":
            self.pop_d()
            self.emit(f"@{5 + index}", "M=D")
        elif segment == "pointer":
            self.pop_d()
            self.emit(f"@{3 + index}", "M=D")
        elif segment == "static":
            self.pop_d()
            self.emit(f"@{self.current_file}.{index}", "M=D")
        else:
            raise ValueError(f"不支援的 segment：{segment}")

    def scoped_label(self, label):
        if self.current_function:
            return f"{self.current_function}${label}"
        return label

    def flow(self, command, label):
        label = self.scoped_label(label)

        if command == "label":
            self.emit(f"({label})")
        elif command == "goto":
            self.emit(f"@{label}", "0;JMP")
        elif command == "if-goto":
            self.pop_d()
            self.emit(f"@{label}", "D;JNE")

    def function(self, name, count):
        self.current_function = name
        self.emit(f"({name})")
        for _ in range(count):
            self.emit("D=0")
            self.push_d()

    def call(self, name, count):
        ret = self.unique("RETURN")

        self.emit(f"@{ret}", "D=A")
        self.push_d()

        for segment in ("LCL", "ARG", "THIS", "THAT"):
            self.emit(f"@{segment}", "D=M")
            self.push_d()

        self.emit(
            "@SP", "D=M",
            f"@{count + 5}", "D=D-A",
            "@ARG", "M=D",
            "@SP", "D=M",
            "@LCL", "M=D",
            f"@{name}", "0;JMP",
            f"({ret})"
        )

    def return_command(self):
        self.emit(
            "@LCL", "D=M",
            "@R13", "M=D",
            "@5", "A=D-A", "D=M",
            "@R14", "M=D"
        )

        self.pop_d()

        self.emit(
            "@ARG", "A=M", "M=D",
            "@ARG", "D=M+1",
            "@SP", "M=D"
        )

        for segment in ("THAT", "THIS", "ARG", "LCL"):
            self.emit(
                "@R13", "AM=M-1", "D=M",
                f"@{segment}", "M=D"
            )

        self.emit("@R14", "A=M", "0;JMP")

    def translate_file(self, path):
        self.current_file = path.stem
        self.current_function = ""

        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            command = line.split("//")[0].strip()

            if not command:
                continue

            parts = command.split()
            op = parts[0]

            try:
                if op in (
                    "add", "sub", "neg", "eq", "gt",
                    "lt", "and", "or", "not"
                ):
                    self.arithmetic(op)

                elif op in ("push", "pop"):
                    segment = parts[1]
                    index = int(parts[2])
                    if index < 0:
                        raise ValueError("索引不可為負數")
                    if segment == "pointer" and index > 1:
                        raise ValueError("pointer 索引只能是 0 或 1")
                    if segment == "temp" and index > 7:
                        raise ValueError("temp 索引只能是 0～7")
                    if op == "push":
                        self.push(segment, index)
                    else:
                        self.pop(segment, index)

                elif op in ("label", "goto", "if-goto"):
                    self.flow(op, parts[1])

                elif op == "function":
                    self.function(parts[1], int(parts[2]))

                elif op == "call":
                    self.call(parts[1], int(parts[2]))

                elif op == "return":
                    self.return_command()

                else:
                    raise ValueError(f"未知指令：{op}")

            except (ValueError, IndexError) as error:
                raise ValueError(
                    f"{path.name} 第 {number} 行：{error}"
                ) from error

    def bootstrap(self):
        self.emit("@256", "D=A", "@SP", "M=D")
        self.call("Sys.init", 0)


def main():
    if len(sys.argv) < 2:
        print("用法：python VMTranslator.py <VM檔案或資料夾>")
        return

    source = Path(sys.argv[1])

    if source.is_file() and source.suffix.lower() == ".vm":
        files = [source]
        output = source.with_suffix(".asm")
        bootstrap = False

    elif source.is_dir():
        files = sorted(source.glob("*.vm"))
        output = source / f"{source.name}.asm"
        bootstrap = any(f.stem == "Sys" for f in files)

    else:
        print("錯誤：請指定 .vm 檔案或資料夾")
        return

    if not files:
        print("找不到 .vm 檔案")
        return

    translator = VMTranslator()

    if bootstrap:
        translator.bootstrap()

    for file in files:
        translator.translate_file(file)

    output.write_text(
        "\n".join(translator.lines) + "\n",
        encoding="utf-8"
    )

    print(f"翻譯完成：{output}")
    print(f"共處理 {len(files)} 個 VM 檔案")


if __name__ == "__main__":
    main()