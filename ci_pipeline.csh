#!/bin/tcsh -f
source sourceme.csh
set venv_path = `poetry env info --path`
if ("$path" !~ "${venv_path}/bin") then
    source ${venv_path}/bin/activate.csh
endif

# Test & coverage
echo "Running pytest coverage..."
coverage run -m pytest -q  # > /dev/null
coverage report -m
coverage html

# Style & complexity
echo "Running style and complexity analysis..."
flake8 app/ -qq --statistics --count  # --extend-ignore=E501,W505
# Static type checking
echo "Running type checking..."
mypy

# Documentation
echo "Running auto-documentation..."
#generate class diagram
pyreverse -A -o png app/  #  --ignore frontend
# sphinx
# cd docs; make html


# Cleanup
# rm -rf htmlcov *.png .coverage
