#!/bin/tcsh -f

# Coverage
echo "Running pytest coverage..."
coverage run -m pytest > /dev/null
coverage report -m
coverage html

# Lint & complexity
echo "Running linter and complexity analysis..."
flake8 app/ -qq --statistics --count

# Documentation
echo "Running auto-documentation..."
# class diagram
pyreverse -A -o png --ignore frontend app/
# sphinx
# cd docs; make html


# Cleanup
# rm -rf htmlcov *.png .coverage
