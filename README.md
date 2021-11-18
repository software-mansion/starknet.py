# Development setup
This is an instruction for setting up your local development environment. Instructions may vary depending on the OS you run.

## Development dependencies
- `pyenv` - recommended for installing and switching python versions locally
- `poetry` - Python dependency manager

## Setup
1. `poetry install`

## Setup verification
Make sure to verify output of this command

```
> poetry run python --version
Python 3.7.x
```

## Setup git hooks

Run this snippet to enable lint checks and automatic formatting before commit/push
```
cp pre-push ./.git/hooks/
cp pre-commit ./.git/hooks/
chmod +x ./.git/hooks/pre-commit
chmod +x ./.git/hooks/pre-push
```

# Running tests
## TBD