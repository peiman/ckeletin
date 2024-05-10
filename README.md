# ckeletin

`ckeletin` is a Command Line Interface (CLI) skeleton designed for professionals looking to create production-ready python cli applications. It includes comprehensive examples and best practices to help streamline the development of robust CLI tools.

## Features

- **Structured Project Layout**: Organized to support larger CLI projects with multiple command groups and integration points.
- **Environment Management**: Uses `.env` for environment variable management to keep configurations secure and separate from code.
- **Automated Testing Setup**: Includes configurations for automated testing with examples to ensure reliability.
- **CI/CD Ready**: Ready to integrate with GitHub Actions for continuous integration and deployment, with examples of how to handle secrets securely.

## Setup Instructions

- Copy `.env.template` to `.env`.
- Replace the placeholder values in `.env` with your actual environment variables.

## How It Works

`ckeletin` utilizes a series of Python scripts structured to demonstrate various CLI capabilities:

1. **Command Handling**: Shows how to define and handle different commands and subcommands using [Typer](https://typer.tiangolo.com).
2. **Configuration Management**: Utilizes [Pydantic](https://docs.pydantic.dev/latest/) for robust configuration handling, demonstrating how to validate and manage application settings.
3. **Logging**: Configured to use [Rich](https://rich.readthedocs.io/en/stable/logging.html) to provide detailed logs for debugging and operational monitoring.

### Running the Application

To run the application locally, follow these steps:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python -m mycliapp
```

## Configuring CI/CD with GitHub Actions

To ensure that `ckeletin` works seamlessly in a CI/CD pipeline, follow these setup steps for GitHub Actions:

1. **Set up Workflow**: Define your `.github/workflows/ci.yml` with steps to install dependencies, run tests, and deploy.
2. **Manage Secrets**:
   - Navigate to your GitHub repository’s Settings.
   - Click on Secrets and choose "New repository secret".
   - Add each configuration/setting parameter that your application needs, which you've defined in your `.env` file. For example, add `ADMIN_EMAIL` as a secret with the appropriate value.

### Example Workflow

Here is a basic example of a GitHub Actions workflow setup for running tests:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    - name: Load Environment Variables
      run: |
        echo "ADMIN_EMAIL=${{ secrets.ADMIN_EMAIL }}" >> $GITHUB_ENV
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=mycliapp
```

## Contributing

Contributions are welcome from the community! If you'd like to contribute to `ckeletin`, please fork the repository, create a feature branch, and submit a pull request.
