

pipenv lock -r > images/python_rip/requirements.txt
isort rip && black rip/