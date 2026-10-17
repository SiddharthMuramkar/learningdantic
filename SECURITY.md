# Security policy

## Supported versions

Only the `main` branch. Fixes land there.

## Report a problem privately

Please don't open a public issue for a security problem. Instead:

1. Open this repo's **Security** tab (GitHub may call it "Security and quality").
2. Click **Report a vulnerability**, fill in the form, and submit it.

Only the maintainer, [@SiddharthMuramkar](https://github.com/SiddharthMuramkar), can see your report. GitHub's
guide: [Privately reporting a security vulnerability](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability).

## What's in scope

The course code: `src/`, `scripts/`, `.claude/hooks/`, and CI (`.github/workflows/`).

## What's not in scope

Pydantic AI and Logfire themselves. Please report those upstream, privately:

- Pydantic AI: [security policy](https://github.com/pydantic/pydantic-ai/security/policy)
- Logfire: [security policy](https://github.com/pydantic/logfire/security/policy)

## Keep your keys safe

- Never paste an API key, a Logfire token or the contents of your `.env` file into an issue, a pull request or
  a comment. They are public.
- `.env` is in `.gitignore`. Keep it that way, and never `git add -f` it.
- If a key leaks, rotate it at the provider (revoke it and make a new one) straight away. Deleting the
  comment or commit is not enough.
