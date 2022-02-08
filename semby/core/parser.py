from dataclasses import dataclass
from enum import IntEnum
from typing import NoReturn

from .lexer import Token, tokenise

REGISTERS = ["a", "b", "c", "d"]
LOADS = [f"ld{r}" for r in REGISTERS]
STORES = [f"st{r}" for r in REGISTERS]


class OpCode(IntEnum):
    HLT = 0x00
    LD = 0x01
    ST = 0x02
    STC = 0x03
    DUP = 0x04
    PUSH = 0x05

    JMP = 0x10
    JMPZ = 0x11
    JMPNZ = 0x12
    JMPP = 0x13

    ADD = 0x20
    SUB = 0x21
    DIV = 0x22
    MUL = 0x23
    MOD = 0x24

    OUT = 0x30
    OUTC = 0x31

    MDP = 0x40
    MLD = 0x41
    CPY = 0x42

    TRC = 0xF0
    SRC = 0xF1


@dataclass
class Instruction:
    op: int
    data: bytearray


@dataclass
class Jump:
    op: int
    ref: str


@dataclass
class ParserOptions:
    strict_jumps: bool = True
    source_mapped: bool = True


SINGLE = {
    "dup": OpCode.DUP,
    "add": OpCode.ADD,
    "sub": OpCode.SUB,
    "div": OpCode.DIV,
    "mul": OpCode.MUL,
    "mod": OpCode.MOD,
    "out": OpCode.OUT,
    "outc": OpCode.OUTC,
    "mdp": OpCode.MDP,
    "mld": OpCode.MLD,
    "cpy": OpCode.CPY,
    "trc": OpCode.TRC,
}

JUMP = {
    "jmp": OpCode.JMP,
    "jmpz": OpCode.JMPZ,
    "jmpnz": OpCode.JMPNZ,
    "jmpp": OpCode.JMPP,
}


def fail(reason: str, file: str, line: int) -> NoReturn:
    print(f"[{file}:{line}] {reason}")
    exit(1)


def parse(code: str, file: str, options: ParserOptions = None) -> list[Instruction]:
    instructions: list[Instruction | Jump] = []
    jumps: dict[str, int] = {}
    bcoffset: int = 0

    options = options or ParserOptions()

    tokens = tokenise(code, file)

    for line in tokens:
        if options.source_mapped:
            data = bytearray()

            data += int(line[0].line).to_bytes(4, "little")
            data += len(line[0].file).to_bytes(4, "little")
            data += bytes(line[0].file, "ascii")

            instructions.append(Instruction(op=OpCode.SRC, data=data))
            bcoffset += 1 + len(data)

        match line:
            case (Token(type="sym", value=":"), Token(type="id", value=x)):
                if options.strict_jumps and x in jumps:
                    fail(f"Jump location {x} is defined multiple times.", line[0].file, line[0].line)

                jumps[x] = bcoffset
            case (Token(type="id", value="hlt"),):
                instructions.append(Instruction(op=OpCode.HLT, data=bytearray()))
            case (Token(type="id", value=x),) if x in LOADS:
                instructions.append(Instruction(op=OpCode.LD, data=bytearray([LOADS.index(x) + 1])))
                bcoffset += 2
            case (Token(type="id", value=x),) if x in STORES:
                instructions.append(Instruction(op=OpCode.ST, data=bytearray([STORES.index(x) + 1])))
                bcoffset += 2
            case (Token(type="id", value=x), Token(type="num", value=y)) if x in STORES:
                instructions.append(
                    Instruction(
                        op=OpCode.STC, data=bytearray([STORES.index(x) + 1]) + bytearray(int(y).to_bytes(8, "little"))
                    )
                )
                bcoffset += 10
            case (Token(type="id", value="push"), Token(type="num", value=y)):
                instructions.append(Instruction(op=OpCode.PUSH, data=bytearray(int(y).to_bytes(8, "little"))))
                bcoffset += 9
            case (Token(type="id", value=x), Token(type="id", value=y)) if x in JUMP:
                instructions.append(Jump(op=JUMP[x], ref=y))
                bcoffset += 5
            case (Token(type="id", value=x),) if x in SINGLE:
                instructions.append(Instruction(op=SINGLE[x], data=bytearray()))
                bcoffset += 1

    output = []

    for instruction in instructions:
        if isinstance(instruction, Instruction):
            output.append(instruction)
        else:
            offset = jumps[instruction.ref]
            output.append(Instruction(op=instruction.op, data=bytearray(offset.to_bytes(4, "little"))))

    return output


def compile(instructions: list[Instruction]) -> bytearray:
    output = bytearray()

    for instruction in instructions:
        output += instruction.op.to_bytes(1, "little")
        output += instruction.data

    return output
