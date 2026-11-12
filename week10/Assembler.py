
import sys
from pathlib import Path

# Hack 組合語言指令對照表
COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


def create_symbol_table():
    """建立 Hack 預設符號表"""
    symbols = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576
    }

    for i in range(16):
        symbols[f"R{i}"] = i

    return symbols


def clean_lines(lines):
    """移除註解、空白與空行"""
    commands = []

    for line in lines:
        line = line.split("//")[0]
        line = "".join(line.split())

        if line:
            commands.append(line)

    return commands


def first_pass(commands, symbols):
    """第一輪：記錄標籤對應的指令位址"""
    instructions = []
    address = 0

    for command in commands:
        if command.startswith("(") and command.endswith(")"):
            label = command[1:-1]
            symbols[label] = address
        else:
            instructions.append(command)
            address += 1

    return instructions


def translate_c_instruction(command):
    """將 C 指令轉換成 16 位元機器碼"""
    dest = ""
    jump = ""

    if "=" in command:
        dest, command = command.split("=", 1)

    if ";" in command:
        command, jump = command.split(";", 1)

    comp = command

    # 支援等價的目的暫存器排列，例如 DM 與 MD
    dest = "".join(ch for ch in "AMD" if ch in dest)

    # 支援部分等價運算寫法
    aliases = {
        "A+D": "D+A",
        "M+D": "D+M",
        "A&D": "D&A",
        "M&D": "D&M",
        "A|D": "D|A",
        "M|D": "D|M",
        "1+D": "D+1",
        "1+A": "A+1",
        "1+M": "M+1"
    }

    comp = aliases.get(comp, comp)

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(input_file):
    """讀取 ASM 檔案並產生 HACK 檔案"""
    input_path = Path(input_file)

    if input_path.suffix.lower() != ".asm":
        raise ValueError("輸入檔案必須是 .asm")

    lines = input_path.read_text(encoding="utf-8").splitlines()
    commands = clean_lines(lines)

    symbols = create_symbol_table()

    # 第一輪：處理標籤
    instructions = first_pass(commands, symbols)

    # 第二輪：翻譯指令與處理變數
    machine_code = []
    next_variable_address = 16

    for command in instructions:
        if command.startswith("@"):
            value = command[1:]

            if value.isdecimal():
                address = int(value)
            else:
                if value not in symbols:
                    symbols[value] = next_variable_address
                    next_variable_address += 1

                address = symbols[value]

            if not 0 <= address <= 32767:
                raise ValueError(f"位址超出範圍：{address}")

            machine_code.append(f"{address:016b}")

        else:
            machine_code.append(
                translate_c_instruction(command)
            )

    output_path = input_path.with_suffix(".hack")

    output_path.write_text(
        "\n".join(machine_code) + "\n",
        encoding="utf-8"
    )

    print(f"組譯完成：{output_path}")
    print(f"總共產生 {len(machine_code)} 行機器碼")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方式：python Assembler.py 檔案.asm")
        sys.exit(1)

    try:
        assemble(sys.argv[1])
    except (OSError, ValueError, KeyError) as error:
        print(f"錯誤：{error}")
        sys.exit(1)
