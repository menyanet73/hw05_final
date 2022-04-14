# hw05_final
Сервис Yatube разработанный по архитектуре MVT. Реализованы функции регистрации, создания постов, ,добавления картинки в пост, комментариев.

#### Стек:
Python 3, Django 2.2, pytest

## How start project:

Clone a repository and go to command line:

```sh
git clone git@github.com:menyanet73/hw05_final.git
```

```sh
cd hw05_final
```

Create and activate virtual environment:

```sh
python3 -m venv env
```
For Windows:
```sh
source env/Scripts/activate  
```
For Linux:
```sh
source env/bin/activate  
```

Install dependencies from a file requirements.txt:

```sh
python3 -m pip install --upgrade pip
```

```sh
pip install -r requirements.txt
```

Apply migrations:

```sh
python3 manage.py migrate
```

Start project:

```sh
python3 manage.py runserver
```

service aviable at:
```sh
https://127.0.0.1:8000/
```

admin panel at:
```sh
https://127.0.0.1:8000/admin/
```
