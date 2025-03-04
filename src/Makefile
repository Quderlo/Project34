venv-win:
	python -m venv venv
	venv\Scripts\pip.exe install -r requirements.txt

venv-lin:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt


migrate-win:
	venv\Scripts\python.exe manage.py makemigrations models
	venv\Scripts\python.exe manage.py migrate

migrate-lin:
	venv/bin/python3 manage.py makemigrations models
	venv/bin/python3 manage.py migrate

build-win: venv-win migrate-win

build-lin: venv-lin migrate-lin