"""Course rules that executing a notebook can't catch.

Usage: uv run python scripts/check_notebooks.py [paths...]   (default: notebooks/ and solutions/)
       uv run python scripts/check_notebooks.py --executed [paths...]   (after `pytest --overwrite`)
       uv run python scripts/check_notebooks.py --self-test
"""

import re
import sys
from pathlib import Path

import nbformat

SETUP = "from learningdantic import setup\nMODEL = setup()"
TRACEBACK = "Traceback (most recent call last)"
# Code-cell patterns that break the course's promises (no asyncio, no run_sync, v2 idioms).
BANNED = {
    r"\brun_sync\(": "use `await agent.run(...)` in notebooks (run_sync fails in Jupyter)",
    r"\bevaluate_sync\(": "use `await dataset.evaluate(...)` in notebooks",
    r"\bimport asyncio\b|\basyncio\.": "no asyncio in the course: `await` is all a learner needs",
    r"\bnest_asyncio": "never needed in modern Jupyter",
    r"async with agent\s*:": "agents open their own connections; `async with agent:` is not taught",
    r"\bAsyncClient\b": "use a sync `httpx.Client` with plain `def` tools",
    r"RunContext\[None\]": "write plain `RunContext` (v2 default deps type is object)",
}


def problems(nb) -> list[str]:
    found = []
    code = [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    # ruff's import sorting puts a blank line after the import, so ignore blank lines here.
    first = "\n".join(line for line in code[0][1].splitlines() if line.strip()) if code else ""
    if first != SETUP:
        found.append(f"first code cell must be exactly:\n{SETUP}")
    for i, src in code:
        for pattern, why in BANNED.items():
            if re.search(pattern, src):
                found.append(f"cell {i}: /{pattern}/ — {why}")
    return found


def crashes(nb) -> list[str]:
    """Cells of an executed notebook that crashed.

    An error raised inside `agent.run` can reach Jupyter as printed text instead of an error, so
    nbmake reports the notebook as passing. Reading the saved outputs catches it.
    """
    found = []
    for i, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error" or TRACEBACK in out.get("text", ""):
                found.append(f"cell {i}: crashed ({out.get('ename') or 'a traceback was printed'})")
    return found


def self_test() -> None:
    good = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(SETUP),
            nbformat.v4.new_code_cell("r = await agent.run('hi')"),
        ]
    )
    bad = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell("import asyncio\nagent.run_sync('hi')")]
    )
    assert problems(good) == [], problems(good)
    assert len(problems(bad)) == 3, problems(bad)  # setup missing + asyncio + run_sync
    printed = nbformat.v4.new_output("stream", name="stderr", text=f"{TRACEBACK}:\nValueError")
    good.cells[1].outputs = [nbformat.v4.new_output("stream", name="stdout", text="hi")]
    assert crashes(good) == [], crashes(good)
    good.cells[1].outputs.append(printed)
    assert len(crashes(good)) == 1, crashes(good)
    print("self-test ok")


def main(args: list[str]) -> int:
    if args == ["--self-test"]:
        self_test()
        return 0
    check = problems
    if args[:1] == ["--executed"]:
        check, args = crashes, args[1:]
    paths = [Path(a) for a in args] or sorted(Path().glob("notebooks/*.ipynb")) + sorted(
        Path().glob("solutions/*.ipynb")
    )
    failed = 0
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        for problem in check(nb):
            print(f"{path}: {problem}")
            failed += 1
    print(f"checked {len(paths)} notebooks, {failed} problem(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
