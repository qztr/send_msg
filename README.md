
## Задача
Отложенное выполнение функции (рассылка сообщений) для группы лиц основываясь на часовом поясе.

## Вводные данные
1.  Предложите решение задачи двумя способами. Выберете один для реализации. Решение должно быть реализовано средствами python.

2.  Есть база данных, в которой имеется следующие данные:

>
| suppliers\_db.phone |  suppliers\_db.name  | district\_db.name  |
|---|---|---|
| +7 000 000 00 00   | ООО «Ромашка»  |  Воронежская  |
| +7 000 000 00 11   | ООО «Пупучик»  |  Амурская  |

3. Есть  модели sqlalchemy



```py
class Supplier(db.Model):
    __tablename__ = 'supplier'
    name = Column(TEXT(None, 'Cyrillic_General_CI_AS'), nullable=True)
    contact_person = Column(TEXT(None, 'Cyrillic_General_CI_AS'), nullable=True)
    inn = Column(String(15, 'Cyrillic_General_CI_AS'), nullable=True)
    storage_address = Column(TEXT(None, 'Cyrillic_General_CI_AS'))
    phone = Column(String(255, 'Cyrillic_General_CI_AS'))
    id = Column(Integer, primary_key=True)
    subscription_cancelled = Column(BIT, nullable=True, comment="Отписан ли от рассылки")
    subscription_admin = Column(BIT, nullable=True, comment="Отписан ли от рассылки админом")
    district_id = Column(ForeignKey('district.id'), nullable=True, comment="id области")
    district = relationship('District')
    area_id = Column(ForeignKey('area.id'), nullable=True, comment="id района")
    area = relationship('Area')
    manager_id = Column(ForeignKey('user.id'), nullable=True)
    manager = relationship('User')
    land_crop = relationship('LandCrop', secondary=supplier_land_crop, backref=backref('suppliers'))
    landuser = Column(String(255, 'Cyrillic_General_CI_AS'), nullable=True)

class District(db.Model):
    __tablename__ = 'district'
    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'Cyrillic_General_CI_AS'), nullable=False, comment="Название области")
```


4. Есть список часовых поясов, в форме словаря {3:3, 7:9} котором имеются следующие данные:

>
| district\_db.id | utc  |
|---|---|
| 3   | 3  |
| 7   | 9  |  

5. Есть функция, которая запускает рассылку по запросу (но не по расписанию) пользователя.

##  Необходимый результат
    

При поступлении команды, необходимо, чтобы на следующий день в 10:00 началась рассылка по всем поставщикам, в зависимости от их часового пояса.

То есть, чтобы каждый поставщик, в зависимости от своей области, получил сообщение в десять часов по местному времени.

Пример:

В Воронежской области 21.10.2021 года, в 21:50 часов дана команда на рассылку.

В Амурской области в это время 22.10.2021 года 03:50 часов.

Получатели сообщения в Амурской области должны получить сообщение 22.10.2021 года в 10:00 часов (то есть 22.10.2021 в 04:00 часов).

Сервер должен продолжать работать и принимать сообщения.

## Решение
Предложим решение двумя способами. Главное отличие которых заключается в реализации отложенного вызова функции рассылки. Отличия приведены ниже.

**Первый.**
Для отложенного вызова  функции рассылки будем использовать инструменты: crontab - это хронологический демон-планировщик задач или python модуль sched. Время будем рассчитывать строго в UTC(+0). 

**Второй**
Для отложенного вызова  функции рассылки будем использовать инструменты:
Метод sleep() модуля time. Для этого пеердадим вычисленное время до заданного часа рассылки от момента вызова. Время будем рассчитывать серверное UTC(+X). 
*(Выбран для реализации)*

Дальнейший функционал идентичен для обоих методов.
Создадим API-endpoint используя Flask:

>  **/activate_mailing**

Обращение по эндпоинту активирует рассылку.
Flask обращается к базе данных и отправляет в очередь отложенный вызов функции рассылки поставщиков, которые подписаны на рассылку.

Пример использования:
```bash
curl http://127.0.0.1:5000/activate_mailing
```

Пример ответа:
```bash
Mailing activated successfully!
```

Далее Celery + RabbitMQ получат в очередь задачи, которые будут выполнены в определённое время:
>  ...чтобы на следующий день в 10:00 началась рассылка по всем поставщикам...

## Установка & запуск
1. Загружаем image:
```bash
docker pull rabbitmq:3-management
```  
2. Запускаем контейнер:
```bash
docker run --rm -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management
```
3. Устанавливаем зависимости:
```bash
pip install -r requirements.txt
```
4.  В файле *Config.py* изменяем строку так, чтобы она содержала путь до *users.db*:
 ```py
 SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/db/send_msg/users.db'
 ```
 
5. Запускаем Celery из корневой папки решения:
```bash
celery -A run.celery worker --loglevel=info
```
6. В новой вкладке консоли запускаем Flask:
```bash
python3 run.py
```
7. Теперь можем обратиться к эндпоинту запуска рассылки в 10 утра на  следующие сутки:
```bash
curl http://127.0.0.1:5000/activate_mailing
```

## Заключение
Задание полностью выполнено. Необходимый результат достигнут в соответствии с поставленной задачей и вводными данными.
Для решения были использованы:
Библиотеки Python:
`amqp==5.0.6
billiard==3.6.4.0
black==21.12b0
celery==5.2.1
click==8.0.3
click-didyoumean==0.3.0
click-plugins==1.1.1
click-repl==0.2.0
flake8==4.0.1
Flask==2.0.2
Flask-SQLAlchemy==2.5.1
greenlet==1.1.2
itsdangerous==2.0.1
Jinja2==3.0.3
kombu==5.2.2
MarkupSafe==2.0.1
mccabe==0.6.1
mypy-extensions==0.4.3
pathspec==0.9.0
pause==0.3
platformdirs==2.4.0
prompt-toolkit==3.0.23
pycodestyle==2.8.0
pyflakes==2.4.0
python-dotenv==0.19.2
pytz==2021.3
six==1.16.0
SQLAlchemy==1.4.27
tomli==1.2.2
typing-extensions==4.0.1
vine==5.0.0
wcwidth==0.2.5
Werkzeug==2.0.2
`
Docker version 20.10.8, build 3967b7d
Docker image *rabbitmq:3-management*

## Комментарий
Возможные улучшения. Для автономной развёртки данный сервис можно реализовать с помощью docker-compose, используя для этого соответствующие контейнеры - Nginx, Flask, Celery, PostgreSQL, RabbitMQ в общей подсети. 

Сервис имеет возможность расширения функционала в целях отправки сообщений в динамический указанное время. Для этого стоит создать новый эндпоинт с аргументом 
/activate_mailing_custom/h=<x>, где x - указанное время отправки.
	
В данном сервисе используется sqlite, а так же БД с заполненными данными - users.db
