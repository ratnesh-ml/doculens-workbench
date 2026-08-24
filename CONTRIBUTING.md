# Contributing

Thanks for helping improve DocuLens Workbench. Keep changes small, explain the retrieval or evaluation trade-off, and include a regression test for changed behaviour.

Before opening a pull request, run:

```bash
pip install -e ".[dev]"
python -m compileall -q src
pytest -q
```

Use synthetic or permission-cleared documents only. Do not commit private documents, credentials, generated indexes containing sensitive text, or copied code from projects whose licenses do not permit reuse. Update the README when a command, API field, evaluation rule, or limitation changes.
