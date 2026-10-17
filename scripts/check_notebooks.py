"""Course rules that executing a notebook can't catch.

Usage: uv run python scripts/check_notebooks.py [paths...]   (default: notebooks/ and solutions/)
       uv run python scripts/check_notebooks.py --self-test
"""

import re
import sys
from pathlib import Path

import nbformat

SETUP = "from learningdantic import setup\nMODEL = setup()"
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
    print("self-test ok")


def main(args: list[str]) -> int:
    if args == ["--self-test"]:
        self_test()
        return 0
    paths = [Path(a) for a in args] or sorted(Path().glob("notebooks/*.ipynb")) + sorted(
        Path().glob("solutions/*.ipynb")
    )
    failed = 0
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        for problem in problems(nb):
            print(f"{path}: {problem}")
            failed += 1
    print(f"checked {len(paths)} notebooks, {failed} problem(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
