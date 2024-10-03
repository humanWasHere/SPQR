# Delivery Procedure
SPQR CLI app deployed with Poetry

### I. Dev env usage
1. Install or update dependencies in a local `.venv/` using poetry:
```bash
poetry install
```
2. Source external dependencies by running `source sourceme.csh` which adds RET and MOA libraries to the `PYTHONPATH`. On Crolles CP domain, it is equivalent to:
```shell
setenv PYTHONPATH /work/retprod/src/pythonlib
source /sw/st/itcad/setup/global/sw -set .ucdprod
```
3. Activate the virtual environment with `poetry shell` or prepend every following command with `poetry run <command>`

### II. Dev env deployment preparation
#### Run QA

The QA flow can be executed in batch with the `ci_pipeline.csh` executable or with the following series of commands. All tools are preconfigured through the `pyproject.toml` file.

Verify all unit tests, integration tests and end-to-end tests are passing.  
```bash
poetry run pytest
```

Check coverage
```bash
poetry run pytest --cov=app
```

Style and complexity linters
```bash
poetry run flake8 --statistics --extend-ignore=E501,W505
```

Type checking
```bash
poetry run mypy
```

Increment project's version in `pyproject.toml`
```ini
[tool.poetry]
...
version = "1.0.0"
```

#### Git modifications checkup
```bash
git status
git diff
```

<!-- #### Upgrade dependencies (if needed)
```bash
poetry update
``` -->

#### Commit and push modifications
```bash
git add .
git commit -m "<commit_name>"
```

#### Version qualification in git
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### III. Production deployment (current)
* Pull deployable version
```bash
git pull origin main
```

* Update `.env` file if needed
```properties
ENVIRONMENT=production
...
```

#### Dependency update
<!-- #### Using same portable environment -->
```bash
poetry install --no-root
```

### III. Production deployment (future pipeline)
Building installs it locally (package not published).
This part is meant to change since CI/CD scripts are comming up

#### Building the package
```bash
poetry build
```
```bash
poetry pip install --user dist/spqr-0.2.1-py3-none-any.whl
```

#### Environment variables
Adding environment variables through a bash script like :
```bash
#!/bin/bash

# Set environment variables
export SECRET_KEY="your_production_secret_key"
export DEBUG=False
```

### IV. Post-deployment verifications
Run the package
```bash
spqr -h
```

Functional testing
```bash
spqr test -a
```

<!-- #### Maintainablity and log monitoring

```bash
tail -f spqr.log*
``` -->

### V. Documentation update
In Development environment
#### Code documentation
Update manual documentation in the `docs` directory **before** integration and mirror it on Sharepoint Online.
* README.md  
* technical documentation  
* users' documentation 

<!-- ```bash
poetry run sphinx-quickstart
poetry run sphinx-build -b html docs/ docs/_build/
``` -->

Update sphinx documentation in Development <u>and</u> Production environments.
```{code} sh
rm -rf docs/_apidoc
sphinx-apidoc --module-first --separate -o docs/_apidoc app
cd docs
make clean html
```

Check documentation at: `firefox docs/_build/html/index.html`

### VI. Communication
Update team through :
* release notes
* meetings
* weekly slides

#### Sphinx/myst test snippet
```{code-block} python
:filename: test.py
:lineno-start: 10
:emphasize-lines: 3
a = 2
print('my 1st line')
print(f'my {a}nd line')
```

<!-- environement variables -->
