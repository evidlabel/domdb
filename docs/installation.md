# Installation

## Prerequisites

- Python 3.12+
- Poetry (package manager)
- Username and password from [Domsdatabasen](https://domsdatabasen.dk/) to access the domsdatabasen.dk API

## Install domdb

1. Clone the repository:
```bash
git clone https://github.com/evidlabel/domdb.git
cd domdb
```

2. Install dependencies:
```bash
poetry install
```

3. Set environment variables:
```bash
export DOMDB_USER_ID="your_user_id"
export DOMDB_PASSWORD="your_password"
```

## Verify Installation

```bash
poetry run domdb --help
```
