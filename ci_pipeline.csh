#!/bin/tcsh -f

# Coverage
echo "Running pytest coverage..."
coverage run -m pytest tests > /dev/null
coverage report -m
coverage html

# Lint & complexity
echo "Running linter and complexity analysis..."
flake8 app/ -qq --statistics --count  # --extend-ignore=E501,W505

# Documentation
echo "Running auto-documentation..."
# class diagram
pyreverse -A -o png app/  #  --ignore frontend
# sphinx
# cd docs; make html
# cd sphinx; make apidoc; make html


# Cleanup
# rm -rf htmlcov *.png .coverage
