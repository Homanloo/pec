# PEC: Phase Equilibrium Calculator

Phase equilibrium calculations for multicomponent mixtures with cubic equations of state:
saturation pressures, bubble and dew points, flash, and phase diagrams, as a Python library,
a documented web API and a web app.

> Being rebuilt from scratch. The original version (B.Sc. thesis, Sharif University of
> Technology, 2024) is in the git history before this rewrite.

## Layout

| Path | What |
|---|---|
| `backend/core/` | `pec`: the thermodynamics library (numpy and scipy only) |

## Development

Needs [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just).

```sh
uv sync      # Python 3.15 and locked dependencies into .venv
just         # list recipes
just check   # lint, type check, tests with coverage, dependency audit
```

## License

MIT
