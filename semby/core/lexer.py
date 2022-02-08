from dataclasses import dataclass
from re import compile

IDENTIFIER = compile(r"^[a-z]+$")


@dataclass
class Token:
    type: str
    value: str
    line: int
    file: str


def tokenise(code: str, file: str) -> list[list[Token]]:
    lines: list[list[Token]] = []

    for i, line in enumerate(code.split("\n")):
        line = line.split()
        out_line: list[Token] = []

        for part in line:
            if part.startswith(";"):
                break

            if part in ".:":
                out_line.append(Token("sym", part, i + 1, file))
            elif IDENTIFIER.match(part):
                out_line.append(Token("id", part, i + 1, file))
            elif part.isdigit():
                out_line.append(Token("num", part, i + 1, file))
            else:
                raise SyntaxError(f"[{file}:{i+i}] Unknown token: " + part)

        if out_line:
            lines.append(out_line)

    return lines
