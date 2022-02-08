from pathlib import Path

from .parser import OpCode


def trace(ptr: int, code: bytearray, stack: list[int], registers: dict[int, int], memory: list[int], name: str = "") -> None:
    output = "--- CODE ---\n"

    for i in range(len(code) // 16 + 1):
        output += " ".join([hex(ins)[2:].zfill(2) for ins in code[i * 16 : (i + 1) * 16]]) + "\n"

    output += "\n--- STACK ---\n"

    for item in stack:
        output += str(item) + "\n"

    output += "\n--- REGISTERS ---\n"

    for key, value in registers.items():
        output += f"{chr(96 + key)}: {value}\n"

    output += f"PTR: {ptr}\n"

    output += "\n--- MEMORY ---\n"

    for i in range(len(memory) // 16 + 1):
        output += " ".join([hex(ins)[2:].zfill(2) for ins in memory[i * 16 : (i + 1) * 16]]) + "\n"

    Path(f"{name + '.' if name else ''}semby.trace").write_text(output)

def execute(code: bytearray, memsize: int = 256, use_trace: bool = False, reraise: bool = False) -> None:
    stack: list[int] = []
    registers: dict[int, int] = {}
    memory: list[int] = [0] * memsize

    ptr = 0

    source_map = [0, "No sourcemap available."]

    try:
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
                print(stack.pop(), end="")
                ptr += 1
            elif instr == OpCode.OUTC:
                print(chr(stack.pop()), end="")
                ptr += 1
            elif instr == OpCode.MDP:
                loc = stack.pop()
                val = stack.pop()
                memory[loc] = val
                ptr += 1
            elif instr == OpCode.MLD:
                stack.append(memory[stack.pop()])
                ptr += 1
            elif instr == OpCode.CPY:
                loc_from = stack.pop()
                loc_to = stack.pop()
                memory[loc_to] = memory[loc_from]
                ptr += 1
            elif instr == OpCode.TRC:
                if use_trace:
                    trace(ptr, code, stack, registers, memory)
                ptr += 1
            elif instr == OpCode.SRC:
                ptr += 1
                line = int.from_bytes(code[ptr: ptr + 4], "little")
                ptr += 4
                datalen = int.from_bytes(code[ptr: ptr + 4], "little")
                ptr += 4
                source_map = [line, str(code[ptr: ptr + datalen], "ascii")]
                ptr += datalen
            else:
                print("Invalid opcode: ", instr)
                exit(1)
    except Exception as e:
        print(f"\nFAILED:\n  Error at {source_map[1]}[{source_map[0]}]")

        if isinstance(e, IndexError):
            print("  Stack underflow.")

        trace(ptr, code, stack, registers, memory, "CRASH")
        if reraise:
            raise e
        exit(1)
