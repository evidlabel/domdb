# Installation

## Prerequisites

- Python 3.12+
- UV (package manager, install via `pip install uv` or from https://docs.astral.sh/uv/)
- Username and password from [Domsdatabasen](https://domsdatabasen.dk/) to access the domsdatabasen.dk API

## Install domdb

1. Clone the repository:
```bash
uv pip install https://github.com/evidlabel/domdb.git
```

2. Set environment variables:
```bash
export DOMDB_USER_ID="your_user_id"
export DOMDB_PASSWORD="your_password"
```

## Verify Installation

```bash
uv run domdb --help
```
