# Installation

## Prerequisites

- Python 3.12+
- UV (package manager, install via `pip install uv` or from https://docs.astral.sh/uv/)
- Username and password from [Domsdatabasen](https://domsdatabasen.dk/) to access the domsdatabasen.dk API

## Install domdb

1. Clone the repository:
```bash
git clone https://github.com/evidlabel/domdb.git
cd domdb
```

2. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix-like systems; use .venv\Scripts\activate on Windows
uv sync
```

3. Set environment variables:
```bash
export DOMDB_USER_ID="your_user_id"
export DOMDB_PASSWORD="your_password"
```

## Verify Installation

```bash
uv run domdb --help
```
