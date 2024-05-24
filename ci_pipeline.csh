#!/bin/tcsh -f
source sourceme.csh

# Test coverage
echo "Running pytest coverage..."
coverage run -m pytest -q  # > /dev/null
coverage report -m
coverage html

# Lint & complexity
echo "Running style and complexity analysis..."
flake8 app/ -qq --statistics --count  # --extend-ignore=E501,W505
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
