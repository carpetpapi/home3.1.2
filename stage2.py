import argparse
import sys
import re
from typing import List, Dict

COMMAND_SPECS = {
    'load_const': {'A': 121, 'size': 2, 'B_bits': 9},
    'read_mem':   {'A': 52,  'size': 3, 'B_bits': 16},
    'write_mem':  {'A': 18,  'size': 5, 'B_bits': 27},
    'bswap':      {'A': 15,  'size': 5, 'B_bits': 27},
}

MNEMONICS = set(COMMAND_SPECS.keys())
CMD_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]*)\s*\)\s*(?:#.*)?$")
def parse_number(token: str) -> int:
    token = token.strip()
    if token.lower().startswith('0x'):
        return int(token, 16)
    return int(token)

def parse_asm(lines):
    ir = []
    for lineno, raw in enumerate(lines, start=1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue

        m = CMD_RE.match(line)
        if not m:
            raise SyntaxError(f"синтаксическая ошибка в строке {lineno}: {raw}")

        mnemonic, arg = m.group(1).lower(), m.group(2).strip()
        if mnemonic not in MNEMONICS:
            raise SyntaxError(f"неизвестная команда '{mnemonic}' в строке {lineno}")

        try:
            B = parse_number(arg)
        except:
            raise SyntaxError(f"отсутствует аргумент для {lineno}: {arg}")

        spec = COMMAND_SPECS[mnemonic]

        if B >= (1 << spec['B_bits']):
            raise ValueError(f"аргумент {B} не помещается в {spec['B_bits']} бит для {mnemonic} в строке {lineno}")

        entry = {
            'mnemonic': mnemonic,
            'A': spec['A'],
            'B': B,
            'size': spec['size'],
            'lineno': lineno,
            'src': raw.strip(),
        }
        ir.append(entry)
    return ir

def encode_instruction(entry: Dict) -> List[int]:
    A = entry['A'] & 0x7F
    B = entry['B']
    size = entry['size']
    word = (B << 7) | A
    out = []
    for i in range(size):
        out.append((word >> (i * 8)) & 0xFF)
    return out

def assemble(ir: List[Dict]) -> List[int]:
    binary = []
    for entry in ir:
        binary.extend(encode_instruction(entry))
    return binary

def main(argv=None):
    parser = argparse.ArgumentParser(description="UVM assembler — Stage 2")
    parser.add_argument("src", help="source .asm file")
    parser.add_argument("out", help="output binary file (.bin)")
    parser.add_argument("--test", action="store_true", help="показать биты")
    args = parser.parse_args(argv)

    try:
        with open(args.src, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"невозможно открыть {args.src}: {e}")
        sys.exit(1)

    try:
        ir = parse_asm(lines)
    except SyntaxError as e:
        print(e)
        sys.exit(2)

    binary = assemble(ir)

    try:
        with open(args.out, 'wb') as f:
            f.write(bytes(binary))
    except Exception as e:
        print(f"невозможно записать {args.out}: {e}")
        sys.exit(3)

    print(f"бинарный файл записан: {args.out}")
    print(f"размер: {len(binary)} байт")

    if args.test:
        print("\nзакодированные байты:")
        print(', '.join(f"0x{b:02X}" for b in binary))


if __name__ == '__main__':
    main()
