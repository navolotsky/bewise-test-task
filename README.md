# Тестовое задание от Bewise.ai: POST-endpoint + контейнеризация (Docker Compose)
Написать простой веб-сервис, который:
1. принимает POST-запрос
2. получает данные (запрошенное количество вопросов) по API от jservice.io
3. пытается сохранить полученное в БД
4. если полученные данные не уникальны, повторяет предыдущие два шага
5. запрашивающему из шага №1 возвращает последний сохраненный *до момента получения от него запроса* вопрос

## Разворачивание для разработки
1. [Установить](https://docs.docker.com/compose/install/) Docker Engine и Docker Compose для вашей ОС
2. Клонировать этот репозиторий: </br>
    ```shell
    git clone https://github.com/navolotsky/bewise-test-task.git
    ```
   Если не установлен `git`, то можно так:
    ```shell
   docker run --name nbewise_repo alpine/git clone https://github.com/navolotsky/bewise-test-task.git &&
   docker cp nbewise_repo:/git/bewise-test-task/ . &&
   docker rm nbewise_repo
    ```
3. Перейти в папку проекта 
    ```shell
   cd bewise-test-task
   ```
4. Запустить сервисы (образ приложения будет собран автоматически)
    ```shell
   docker compose up
   ```
5. Можно выполнять POST-запросы на `http://localhost:8000`
6. При изменении исходников в папке `bewise_test_task` dev-сервер будет перезапускаться автоматически
7. При внесении изменений в `Dockerfile` не забывать пересобирать образ приложения
    ```shell
   docker compose build
   ```
   А затем перезапускать сервисы
    ```shell
   docker compose up
   ```

## API
POST-запросы на `/` c json-телом вида `{"questions_num": integer}`

## Примеры запросов
```python
>>> import requests
>>> from pprint import pprint
>>> 
>>> # первый запрос с пустой БД
>>> response = requests.request("POST", "http://localhost:8000", json={"questions_num": 3})
>>> pprint(response.json())
{'last_saved_question': {}}
>>>
>>> # возвращает последний сохраненный в БД вопрос
>>> response = requests.request("POST", "http://localhost:8000", json={"questions_num": 3})
>>> pprint(response.json())
{'last_saved_question': {'airdate': '2000-02-04 12:00:00',
                         'answer': 'Barbara Bush',
                         'created_at': '2014-02-11 23:08:31',
                         'id': 3,
                         'pulled_at': '2022-05-08 20:17:11',
                         'question': 'In 1992 she became the 1st first lady to '
                                     'deliver a major address at a national '
                                     'political convention',
                         'question_id': 37949}}
>>>
>>> # пример ошибки: лимит jservice.io равен 100
>>> response = requests.request("POST", "http://localhost:8000", json={"questions_num": 101})
>>> pprint(response.json())
{'field_errors': {'questions_num': 'must be an integer in the range of [1, '
                                   '100]'}}
>>>
```
