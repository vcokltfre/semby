from pathlib import Path

from typer import Typer, echo

from ..core import compile as compile_bc
from ..core import execute, parse

app = Typer()


@app.command(name="compile")
def compile(file: str, out: str = "out.smbc") -> None:
    data = Path(file).read_text()

    compiled = compile_bc(parse(data, file))

    with Path(out).open("wb") as f:
        f.write(compiled)

    echo(f"Compilation done. Written {len(compiled)} bytes to {out}")


@app.command(name="exec")
def exec(file: str, memsize: int = 256, trace: bool = False) -> None:
    data = Path(file).read_bytes()

    execute(bytearray(data), memsize, trace)


@app.command(name="run")
def run(file: str, memsize: int = 256, trace: bool = False) -> None:
    data = Path(file).read_text()

    compiled = compile_bc(parse(data, file))

    execute(compiled, memsize, trace)
