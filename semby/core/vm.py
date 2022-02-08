from .parser import OpCode


def execute(code: bytearray) -> None:
    stack: list[int] = []
    registers: dict[int, int] = {}

    ptr = 0

    while ptr < len(code):
        instr = code[ptr]

        if instr == OpCode.HLT:
            exit(stack.pop())
        elif instr == OpCode.LD:
            stack.append(registers[code[ptr + 1]])
            ptr += 2
        elif instr == OpCode.ST:
            registers[code[ptr + 1]] = stack.pop()
            ptr += 2
        elif instr == OpCode.STC:
            registers[code[ptr + 1]] = int.from_bytes(code[ptr + 2 : ptr + 10], "little")
            ptr += 10
        elif instr == OpCode.DUP:
            stack.append(stack[-1])
            ptr += 1
        elif instr == OpCode.PUSH:
            stack.append(int.from_bytes(code[ptr + 1 : ptr + 9], "little"))
            ptr += 9
        elif instr == OpCode.JMP:
            ptr = int.from_bytes(code[ptr + 1 : ptr + 5], "little")
        elif instr == OpCode.JMPZ:
            ptr = int.from_bytes(code[ptr + 1 : ptr + 5], "little") if stack.pop() == 0 else ptr + 5
        elif instr == OpCode.JMPNZ:
            ptr = int.from_bytes(code[ptr + 1 : ptr + 5], "little") if stack.pop() != 0 else ptr + 5
        elif instr == OpCode.JMPP:
            ptr = int.from_bytes(code[ptr + 1 : ptr + 5], "little") if stack.pop() > 0 else ptr + 5
        elif instr == OpCode.ADD:
            stack.append(stack.pop() + stack.pop())
            ptr += 1
        elif instr == OpCode.SUB:
            stack.append(stack.pop() - stack.pop())
            ptr += 1
        elif instr == OpCode.DIV:
            stack.append(int(stack.pop() // stack.pop()))
            ptr += 1
        elif instr == OpCode.MUL:
            stack.append(stack.pop() * stack.pop())
            ptr += 1
        elif instr == OpCode.MOD:
            stack.append(stack.pop() % stack.pop())
            ptr += 1
        elif instr == OpCode.OUT:
            print(stack.pop())
            ptr += 1
        elif instr == OpCode.OUTC:
            print(chr(stack.pop()), end="")
            ptr += 1
        else:
            print("Invalid opcode: ", instr)
            exit(1)
