from pathlib import Path
from subprocess import Popen

from typer import Typer, echo

from ..core import compile as compile_bc
from ..core import execute, parse
from ..core.parser import ParserOptions

app = Typer()


@app.command(name="compile")
def compile(file: str, out: str = "out.smbc", sourcemap: bool = True) -> None:
    data = Path(file).read_text()
    opts = ParserOptions(source_mapped=sourcemap)

    compiled = compile_bc(parse(data, file, opts))

    with Path(out).open("wb") as f:
        f.write(compiled)

    echo(f"Compilation done. Written {len(compiled)} bytes to {out}")


@app.command(name="exec")
def exec(file: str, memsize: int = 256, trace: bool = False, reraise: bool = False) -> None:
    data = Path(file).read_bytes()

    execute(bytearray(data), memsize, trace, reraise)


@app.command(name="run")
def run(file: str, memsize: int = 256, trace: bool = False, reraise: bool = False, sourcemap: bool = True, vm: str = "default") -> None:
    data = Path(file).read_text()
    opts = ParserOptions(source_mapped=sourcemap)

    compiled = compile_bc(parse(data, file, opts))

    if vm == "default":
        execute(compiled, memsize, trace, reraise)
    elif vm == "gosemby":
        Path("/tmp/semby.smbc").write_bytes(compiled)
        Popen(["gosemby", "/tmp/semby.smbc"])
    else:
        raise ValueError(f"Unknown VM: {vm}")
