"""PreToolUse hook for Bash: block force-pushes, pushes to main, and admin/auto merges.

Reads the hook JSON on stdin. Exit 2 (with a reason on stderr) blocks the command; any other case,
including a parsing error in this script, exits 0 so a hook bug never stalls the session.
"""

import json
import shlex
import sys

MAIN_REFS = {"main", "HEAD:main", "refs/heads/main"}


def segments(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    parts, current = [], []
    for token in lexer:
        if token in {"&&", "||", ";", "|", "&", ";;"}:
            parts.append(current)
            current = []
        else:
            current.append(token)
    return [*parts, current]


def push_problem(args: list[str]) -> str | None:
    for arg in args:
        if arg.startswith("--force") or arg == "-f":
            return "force-push"
        if arg.startswith("-") and not arg.startswith("--") and "f" in arg[1:]:
            return "force-push"
        if arg.startswith("+"):
            return "forced refspec"
        if arg in MAIN_REFS or arg.endswith((":main", ":refs/heads/main")):
            return "push to main (open a PR instead)"
    return None


def reason(command: str) -> str | None:
    for seg in segments(command):
        for i, token in enumerate(seg):
            if token == "git":
                rest = seg[i + 1 :]
                while rest[:1] and rest[0] in {"-C", "-c"}:  # skip `git -C path`, `git -c k=v`
                    rest = rest[2:]
                if rest[:1] == ["push"] and (why := push_problem(rest[1:])):
                    return why
            if seg[i : i + 3] == ["gh", "pr", "merge"] and {"--admin", "--auto"} & set(seg[i:]):
                return "admin/auto merge (merge only after CI is green)"
    return None


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
        why = reason(command)
    except Exception:
        return 0  # fail open
    if why:
        print(f"Blocked by .claude/hooks/guard_git.py: {why}.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
