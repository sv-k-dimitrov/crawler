# Developer Guide

## Requirements

### Infrastructure

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [PostgreSQL](https://www.postgresql.org/download/)

### Python

version: 3.12^

**Utils:**

- [pipx](https://pipx.pypa.io/stable/installation/) - this package manager will be used to ease the process for installing/ upgrading `poetry`
- [poetry](https://python-poetry.org/) - virtual environment package manager

**VSCode plugins:**

- https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring
- https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter
- https://marketplace.visualstudio.com/items?itemName=ms-python.flake8
- https://marketplace.visualstudio.com/items?itemName=ms-python.isort
- https://marketplace.visualstudio.com/items?itemName=ms-python.python
- https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide

**Poetry Settings:**

Following settings should be configured once `poetry` is available.

- `$: poetry config virtualenvs.path "{project-dir}/.venv"`
- `$: poetry config virtualenvs.in-project true`

## IDE

Following VSCode **user** settings, should be added.

```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "always"
    }
  },
  "isort.args": ["--profile", "black"],
  "isort.importStrategy": "fromEnvironment",
  "flake8.importStrategy": "fromEnvironment",
  "flake8.cwd": "${workspaceFolder}/crawler"
}
```

## Local Setup

### AWS CLI

TBD

### Python

```bash
$: cd crawler
$: poetry env use python3.12 # or any other suitable version
$: poetry shell # to open new terminal session within the virtual environment
$: poetry install # will install all required packages
```

Once all of the above commands are executed ensure to select the new interpreter as default for the VSCode project.

### Post Setup
- Create env file with database connection settings:
- DATABASE_NAME=database_name
- DATABASE_USER=databae_user
- DATABASE_PASSWORD="database password"
- DATABASE_HOST=database host
- DATABASE_PORT=database port
- 

- ensure you've configured all `pre-commit` hooks using `make project-setup`.
- use the `.env.example` to refer to your local database configuration
- ensure you've applied all existing ORM migrations using `make local-db-setup`
