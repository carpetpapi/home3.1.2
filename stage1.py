import argparse
import re
import sys
from typing import List

MNEMONICS = {"load_const", "read_mem", "write_mem", "bswap"}
CMD_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s*(?:#.*)?$")
def parse_number(token: str) -> int:
    token = token.strip()
    return int(token, 0) 


def parse_asm(lines: List[str]):
    ir = []
    for lineno, raw in enumerate(lines, start=1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue

        m = CMD_RE.match(line)
        if not m:
            raise SyntaxError(f"Ошибка синтаксиса в строке {lineno}: {raw!r}")

        mnemonic = m.group(1).lower()
        if mnemonic not in MNEMONICS:
            raise SyntaxError(f"Неизвестная команда '{mnemonic}' в строке {lineno}")

        arg = parse_number(m.group(2))

        ir.append((mnemonic, arg, raw.strip(), lineno))

    return ir


def print_ir(ir):
    print("IR:\n")
    for mnemonic, arg, src, lineno in ir:
        print(f"{lineno:>2}: {src}")
        print(f"  mnemonic = {mnemonic}")
        print(f"  B = {arg}\n")


def main():
    parser = argparse.ArgumentParser(description="UVM assembler – stage 1")
    parser.add_argument("src", help="asm input")
    parser.add_argument("out", help="ir output")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    try:
        lines = open(args.src, "r", encoding="utf8").readlines()
    except Exception as e:
        print(f"не удалось открыть {args.src}: {e}")
        sys.exit(2)

    try:
        ir = parse_asm(lines)
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}")
        sys.exit(3)

    if args.test:
        print_ir(ir)
        return

    with open(args.out, "w", encoding="utf8") as f:
        for mnemonic, arg, _, _ in ir:
            f.write(f"{mnemonic} {arg}\n")

    print(f"IR записан в {args.out}")


if __name__ == "__main__":
    main()
