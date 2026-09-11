# Contributing

Contributions are welcome through GitHub pull requests. Report suspected
vulnerabilities through the private process in `SECURITY.md`.

Before changing the repository, read `CLAUDE.md`, `docs/ROADMAP.md`,
`docs/SUPPORT.md`, and `docs/VERSION.md`. Keep runtime additions minimal, pin
external inputs, and never commit credentials or database contents. Behavior
changes require matching tests, operator guidance, security review, and a
changelog entry.

Run repository checks with:

```console
python -m pip install --require-hashes --only-binary=:all: \
  --requirement .github/requirements/pre-commit.txt
pre-commit run --all-files --show-diff-on-failure
```

Image changes must also pass the build and smoke commands in `README.md`.
Use concise Conventional Commit subjects and never add AI, assistant, tool,
or `Co-Authored-By` attribution trailers.
