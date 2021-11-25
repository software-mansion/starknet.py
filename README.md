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

# Tests
### Running tests
```
poe test
```

### Generating report
```
poe test_report
```
or 
```
poe test_html
```

# Example usage

_Warning: Current API is experimental and will be changed in the future_

## Asynchronous API
This is the recommended way of using the SDK.
```
key = 1234
contract = await Contract.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client())
invocation = await contract.functions.set_value.invoke(key, 7)
await invocation.wait_for_acceptance()

saved = await contract.functions.get_value.call(key) # ['0x7']
```


## Synchronous API
You can access synchronous world when using `Contract.sync`.

```
key = 1234
contract = Contract.sync.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client())
invocation = contract.functions.set_value.invoke(key, 7)
invocation.wait_for_acceptance()

saved = contract.functions.get_value.call(key) # ['0x7']
```