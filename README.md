<h1 align="center"><a href="https://lolpaynet.ru" target="_BLANK">Lolpaynet.ru</a></h1>

<br/>


![Python Version](https://img.shields.io/badge/Python-3.12.2-blue)
![Django Version](https://img.shields.io/badge/Django-5.1.1-blue)
![Redis Version](https://img.shields.io/badge/Redis-5.1.1-blue)
![Code Style](https://img.shields.io/badge/code_style-pep8-orange)
![Coverage](https://img.shields.io/badge/coverage-89%-orange)
___

## Содержание

* **[Запуск проекта на локальном компьютере](#запуск-проекта-на-локальном-компьютере)**
* **[Запуск проекта на локальном компьютере через Docker](#запуск-проекта-на-локальном-компьютере-через-docker)**
* **[Deployment проекта на удаленный сервер](#deployment-проекта-на-удаленный-сервер)**
* **[FAQ](#faq)**
___

## Запуск кпроекта на локальном компьютере

**1. Скачайте проект на локальный компьютер**
```
git clone https://github.com/Eclipser03/Lol-pro
```

**2. Создайте виртуальное окружение**
```
python -m venv venv
```

**3. Активируйте виртуальное окружение**

*macOS*
```
. venv/bin/activate
```

*linux*

```
source venv/bin/activate
```

*windows*

```
venv/Scripts/activate
```

**4.Обновите пакетный установщик pip**
```
python -m pip install -upgrade pip
```

**5.Зайдите в рабочую директорию проекта(все дальнейшие действия будут осуществляется в ней)**
```
cd Lol-pro
```

**6. Установите зависимости необходимые для запуска проекта**
```
pip install -r requirements.txt
```

**7. Сгенерируйте статические файлы**
```
python manage.py collectstatic
```

**8. Создайте файлы миграций**
```
python manage.py makemigrations
```

**9. Примините миграции**
```
python manage.py migrate
```

**10. Создайте файл `.env` и заполните его по примеру**
```
SECRET_KEY = 'secret-key'
POSTGRES_DB='dbname'
POSTGRES_USER='dbuser'
POSTGRES_PASSWORD='dbpassword'
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

RECAPTCHA_PUBLIC_KEY = 'public-key'
RECAPTCHA_PRIVATE_KEY = 'private-key'

EMAIL_HOST_PASSWORD = 'email-password-IMAP'
EMAIL_HOST_USER = 'email'


REDIS_HOST = 127.0.0.1
REDIS_PORT = 6379
```

**11. Запустите Redis(Как установить [Redis](https://github.com/tporadowski/redis)?)**
```
redis-server
```

**12.Запустите сервер**
```
python manage.py runserver
```

**13. Для полноценной работы проекта запустите Celery во второй консоли**
```
python manage.py runcelery
```

**14. Откройте проект в браузере по адресу**
```
http://127.0.0.1:8000/
```

**Для остановки сервера нажмите `CTRL+C` или `CMD+C`(для mac) в обеих консолях**

___


## Запуск проекта на локальном компьютере через [Docker](https://www.docker.com/get-started/)

**1. Скачайте проект на локальный компьютер**
```
git clone https://github.com/Eclipser03/Lol-pro
```

**2. Зайдите в рабочую директорию проекта(все дальнейшие действия будут осуществляется в ней)**
```
cd Lol-pro
```

**3. Создайте файл `.env` и заполните его по примеру**
```
SECRET_KEY = 'secret-key'
POSTGRES_DB='dbname'
POSTGRES_USER='dbuser'
POSTGRES_PASSWORD='dbpassword'
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

RECAPTCHA_PUBLIC_KEY = 'public-key'
RECAPTCHA_PRIVATE_KEY = 'private-key'

EMAIL_HOST_PASSWORD = 'email-password-IMAP'
EMAIL_HOST_USER = 'email'


REDIS_HOST = 127.0.0.1
REDIS_PORT = 6379
```

**4. Запустите Docker Desktop на пк.**

**5. Создайте образ и запустите контейнер**
```
docker compose up --build
```

**6. Откройте проект в браузере по адресу**
```
http://127.0.0.1:8000/
```

**Для остановки контейнера нажмите `CTRL+C` или `CMD+C`(для mac) в консоли**

___

# Deployment проекта на удаленный сервер

## Содержание
* **[Вход на удаленный сервер](#remote-access)**
* **[Установка необходимых пакетов из репозитория `Ubuntu`](#install-packages)**
* **[Создание базы данных](#create-db)**
* **[Создание виртуального окружение](#create-venv)**
* **[Настройка Vim](#vim-settings)**
* **[Тестовый запуск](#test-run)**
* **[Настройка Gunicorn](#setup-gunicorn)**
* **[Установка Redis](#setup-redis)**
* **[Установка Daphne](#setup-daphne)**
* **[Установка Celery](#setup-celery)**
* **[Настройка Celery-flower и Celery-beat](#setup-flower_beat)**
* **[Настройка Nginx](#setup-nginx)**
* **[Подключение домена](#setup-domain)**
* **[Настройка HTTPS](#HTTPS-settings)**
* **[Проверка служб](#checking-services)**
___
<a id="remote-access"></a>
* **Войдите на удаленный сервер с помощью `SSH` или `FTP`**

  *linux/macOS*

  ```
  ssh username@server_ip
  ```
  далее введите пароль для подключения.
  <br/>
  *Windows*
  <br/>

  **Для подключения по `SSH` на Windows можно использовать следующее ПО, [Putty](https://www.putty.org/) или [MobaXterm](https://mobaxterm.mobatek.net/)**
<br/><br/>

<a id="install-packages"></a>
* **Установите необходимык пакеты из репозитория `Ubuntu`**

  **1. Обновите список пакетов репозитория**

  ```
  sudo apt update
  ```

  **2. Установите необходимы пакеты**

  ```
  sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
  ```
<br/>

<a id="create-db"></a>
* **Создайте базу данных и пользователя для PostgreSQL**

  **1. Войдите в интерактивный сеанс `Postgres`**

  ```
  sudo -u postgres psql
  ```

  **2. Создайте базу данных**

  ```
  CREATE DATABASE db_name;
  ```

  **3. Создайте пользователя**

  ```
  CREATE USER db_username WITH PASSWORD 'user_password';
  ```

  **4. Установите кодировку `UTF-8`**

  ```
  ALTER ROLE db_username SET client_encoding TO 'utf8';
  ```

  **5. Заблокируйте чтение из незафиксированных транзакций**

  ```
  ALTER ROLE db_username SET default_transaction_isolation TO 'read committed';
  ```

  **6. Установите часовой пояс**

  ```
  ALTER ROLE db_username SET timezone TO 'UTC';
  ```

  **7. Предоставьте пользователю доступ для администрирования БД**

  ```
  GRANT ALL PRIVILEGES ON DATABASE db_name TO db_username;
  ```

  **8.Предоставление всех привилегий на схему public**

  ```
  GRANT ALL PRIVILEGES ON SCHEMA public TO your_database_user;
  ```

  **9.Назначение суперпользователя**

  ```
  ALTER USER your_database_user WITH SUPERUSER;
  ```

  **10. Выйдите из интерактивного режима**

  ```
  \q
  ```
<br/>

<a id="create-venv"></a>
* **Создайте виртуальное окружение для проекта**
  <br/>
  ```
  sudo -H pip3 install --upgrade pip ПОСТАВИТЬ НИЖЕ
  ```
  <br/><br/>

* **Установите `Python-3.12.2`**
<br/>


    **1. Установите необходимые пакеты**
    ```
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev
    ```

    ```
    sudo apt-get install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm
    ```

    ```
    sudo apt-get install -y libncurses5-dev  libncursesw5-dev xz-utils tk-dev
    ```

    **2. Перейдите в каталог `/opt`**

    ```
    cd /opt
    ```

    **3. Скачайте архив с исходным кодом `Python-3.12.2`**

    ```
    wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz
    ```

    **4. Распакуйте архив**

    ```
    tar xzvf Python-3.12.2.tgz
    ```

    **5. Зайдите в разархивированный каталог**

    ```
    cd Python-3.12.2
    ```

    **6. Выполните оптимизацию компилятора при сборке `python`**

    ```
    ./configure --enable-optimizations
    ```

    **7. Скомпилируйте исходные файлы**

    ```
    make
    ```

    **8. Установите скомпилируемые файлы**

    ```
    sudo make install
    ```

    **9. Перейдите в рабочую директорию**

    ```
    cd /root/
    ```
    <br/><br/>

**2. Загрузите файлы проекта на удаленный сервер**
<br/>

*git*

```
git clone https://github.com/Eclipser03/Lol-pro
```

*scp (выполнять на локальном ПК)*

```
scp -r <путь до директории на локальном ПК> [username]@[server_ip]:<путь куда копировать диркторию>
```
*Перейдите в папку с проектом*

```
cd Lol-pro/
```

**3. Создайте виртуальное окружение**

```
python3.12 -m venv venv
```

**4. Активируйте виртуальное окружение**

```
source venv/bin/activate
```

**5. Обновите пакетный установщик `pip`**

```
pip install --upgrade pip
```

**6. Установите зависимости для проекта**

```
pip install -r requirements.txt
```

**7. Дополнительно установите**

```
pip install gunicorn psycopg2-binary
```

**8. Для работы вебсокета установите**

```
pip install -U 'Twisted[tls,http2]'
```
<br/>

<a id="vim-settings"></a>
* **Настройте `vim` для комфортной работы с файлами**
<br/>

  **Перейдите в директорию `root`**

  ```
  cd /root
  ```

  **Создайте файл `.vimrc` с содержимим:**

  ```
  echo 'set tabstop=4
  set shiftwidth=4
  set expandtab
  set relativenumber
  set showmode
  set laststatus=2
  set cursorline
  set mouse=a
  set mousefocus=true
  ' > .vimrc
  ```

  **Вернитесь в рабочую директорию проекта**

  ```
  cd /root/Lol-pro
  ```
<br/>

<a id="test-run"></a>
* **Тестовый запуск проекта**
<br/>

  **1. Разрешите входящий трафик по порту `8000`**

  ```
  sudo ufw allow 8000
  ```
  **2. Создайте файл `.env` и заполните его по примеру**

  ```
  SECRET_KEY = 'secret-key'
  POSTGRES_DB='dbname'
  POSTGRES_USER='dbuser'
  POSTGRES_PASSWORD='dbpassword'
  POSTGRES_HOST=127.0.0.1
  POSTGRES_PORT=5432

  RECAPTCHA_PUBLIC_KEY = 'public-key'
  RECAPTCHA_PRIVATE_KEY = 'private-key'

  EMAIL_HOST_PASSWORD = 'email-password-IMAP'
  EMAIL_HOST_USER = 'email'

  REDIS_HOST = 127.0.0.1
  REDIS_PORT = 6379
  ```

  **2. Создайте файлы миграций**

  ```
  python manage.py makemigrations
  ```

  **3. Примините миграции**

  ```
  python manage.py migrate
  ```

  **4. Откройте файл `settings.py` и измените переменные `ALLOWED_HOSTS`, `DEBUG` `DATABASES`**

  ```
  vim lol_pay/settings/base.py
  ```

  ```python

  ALLOWED_HOST = ['server_ip']
  ```

  ```python

  DEBUG=False
  ```

  *В файле `storage.py`*:
  ```python

  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_name',
        'USER': 'db_username',
        'PASSWORD': 'user_password',
        'HOST': 'localhost',
        'PORT': '',
    }
  }
  ```
  **5. Запустите сервер**

  ```
  python manage.py runserver 0.0.0.0:8000
  ```

  **6. Откройте проект в браузере по адресу**

  ```
  http://<server_ip>:8000/
  ```

  **Для остановки сервера нажмите `CTRL+C` или `CMD+C`(для mac)**
  <br/><br/>

  **Если `static` файлы или `media` файлы не прогружаются - выполните следующие команды:**
  <br/>

  ```
  sudo chown -R www-data:www-data /root/Lol-pro/static
  ```

  ```
  sudo chown -R www-data:www-data /root/Lol-pro/media
  ```

  ```
  sudo chmod -R 777 /root/Lol-pro/static
  ```

  ```
  sudo chmod -R 777 /root/Lol-pro/media
  ```

  ```
  sudo usermod -a -G www-data $(whoami)
  ```

  ```
  python manage.py collectstatic
  ```
  *Что бы в админ панели отображались статические файлы*

  ```
  cp -r staticfiles/* static/
  ```

<br/>

<a id="setup-gunicorn"></a>
* **Создайте systemd socket и service файлы для Gunicorn**
<br/>
  **`Gunicorn` нужен для автозапуска проекта, на случай перезапуска сервера, или если по какой-то причине сервер выходил из строя.**

  <br/>

  **1. Проверьте работоспособность `Gunicorn`**

  ```
  gunicorn --bind 0.0.0.0:8000 lol_pay.wsgi
  ```

  **Для остановки сервера нажмите `CTRL+C` или `CMD+C`(для mac)**

  <br/>

  **Для автозапуска мы будем использовать [systemd](https://en.wikipedia.org/wiki/Systemd)**
  <br/>


  **2. Создайте файл `/etc/systemd/system/gunicorn.socket` со следующим содержимым**

  ```
  vim /etc/systemd/system/gunicorn.socket
  ```

  ```
  [Unit]
  Description=gunicorn socket

  [Socket]
  ListenStream=/run/gunicorn.sock

  [Install]
  WantedBy=sockets.target
  ```

  **3. Создайте файл `/etc/systemd/system/gunicorn.service` со следующим содержимым**

  ```
  [Unit]
  Description=gunicorn daemon
  Requires=gunicorn.socket
  After=network.target

  [Service]
  User=root
  Group=www-data
  WorkingDirectory=/root/Lol-pro
  ExecStart=/root/Lol-pro/venv/bin/gunicorn \
           --access-logfile - \
           --workers 3 \
           --bind unix:/run/gunicorn.sock \
           lol_pay.wsgi:application

  [Install]
  WantedBy=multi-user.target
  ```

  **4. Запустите службу `gunicorn.socket`**

  ```
  sudo systemctl start gunicorn.socket
  ```

  **5. Включите службу `gunicorn.service`**

  ```
  sudo systemctl enable gunicorn.socket
  ```

  **6. Проверьте работу `gunicorn.socket`**

  ```
  sudo systemctl status gunicorn.socket
  ```


  <br/>

  ## Полезные команды

  **При изменении файла `gunicorn.service` - выполните**

  ```
  sudo systemctl daemon-reload
  ```

  **При изменении файлов проекта - выполните**

  ```
  sudo systemctl restart gunicorn
  ```

  **Проверить статус `gunicorn`**

  ```
  sudo systemctl status gunicorn
  ```

  **Посмотреть лог `gunicorn`(все ошибки связанные с запуском сервера, или внутренние ошибки сервера будут там)**

  ```
  sudo journalctl -u gunicorn
  ```
  Для быстрого перемещения можно использовать сочетания клавиш:<br/>
  `SHIFT+G` - перейти в конец<br/>
  `G` - перейти в начало<br/>
  `q` - выход
  <br/><br/>

<a id="setup-redis"></a>
* **Установка и настройка `Redis`**
    <br/><br/>

  **1. Разрешите входящий трафик по порту `6379`**

  ```
  sudo ufw allow 6379
  ```

  **2. Установите `Redis`**

  ```
  sudo apt install redis-server
  ```

  **3. Для автозапуска `Redis` в файле `/etc/redis/redis.conf` замените `supervised no` на `supervised systemd`**

  ```
  vim /etc/redis/redis.conf
  ```

  **4. Перезапустите `Redis`**

  ```
  sudo systemctl restart redis.service
  ```

  **5. Проверьте работу `Redis`**

  ```
  sudo systemctl status redis
  ```

  **Так же вы можете проверить работу `Redis` и не только с помощью**

  ```
  sudo apt install net-tools
  ```

  ```
  sudo netstat -lnp | grep redis
  ```
<br/>

<a id="setup-daphne"></a>
* **Установка и настройка `Daphne` для работы `WebSocket`**

  **1. Установите `Daphne`**

  ```
  sudo apt install daphne
  ```

  **2. Создайте файл `/etc/systemd/system/daphne.service` со следующим содержимым**

  ```
  vim /etc/systemd/system/daphne.service
  ```

  ```
  [Unit]
  Description=WebSocket Daphne Service
  After=network.target

  [Service]
  Type=simple
  User=root
  WorkingDirectory=/root/Lol-pro
  ExecStart=/root/Lol-pro/venv/bin/python /root/Lol-pro/venv/bin/daphne -b 0.0.0.0 -p 8001 lol_pay.asgi:application
  Restart=on-failure

  [Install]
  WantedBy=multi-user.target

  ```

  **3. Примените изменения**

  ```
  sudo systemctl daemon-reload
  ```

  **4. Запустите службу `daphne.servie`**

  ```
  sudo systemctl start daphne.service
  ```

  **5. Проверьте слежбу `daphne.service`**

  ```
  sudo systemctl status daphne.service
  ```

  **6. Для автозапуска `Daphne` создайте файл `/root/boot.sh` со следующим содержимым**

  ```
  vim /root/boot.sh
  ```

  ```
  #!/bin/sh
  sudo systemctl start daphne.service
  ```

  **7. Установите запуск этого файла как скрипт**

  ```
  chmod u+x /root/boot.sh
  ```

  **8. Сообщите `systemd`, чтобы он запускал `/root/boot.sh` при перезагрузке сервера**

  ```
  vim /etc/systemd/system/on_boot.service
  ```

  ```
  [Service]
  ExecStart=/bin/bash /root/boot.sh

  [Install]
  WantedBy=default.target
  ```

  **9. Перезагрузите конфигурацию `systemd`**

  ```
  sudo systemctl daemon-reload
  ```

  **10. Запустите службу `on_boot`**

  ```
  sudo systemctl start on_boot
  ```

  **11. Включите службу `on_boot`**

  ```
  sudo systemctl enable on_boot
  ```

  **12. Разрешите входящий трафик по порту 8001**

  ```
  sudo ufw allow 8001
  ```

  **13. Перезапустите сервер**

  ```
  sudo shutdown -r now
  ```

  **14. Проверьте состояние следующих служб**

  ```
  systemctl status on_boot.service
  ```

  ```
  systemctl status daphne.service
  ```

  ```
  systemctl status gunicorn.service
  ```
  <br/>

<a id="setup-celery"></a>
* **Установка и настройка `Celery Worker`**
<br/>

  **1. Установите `Celery`**

  ```
  sudo apt -y install celery
  ```

  **2. Создайте файл `/etc/systemd/system/celery.service` со следующим содержимым**

  ```
  vim /etc/systemd/system/celery.service
  ```

  ```
  [Unit]
  Description=Celery Service
  After=network.target

  [Service]
  Type=forking
  User=root
  Group=www-data
  EnvironmentFile=/etc/conf.d/celery
  WorkingDirectory=/root/Lol-pro
  ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
    -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
    --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
  ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
    --pidfile=${CELERYD_PID_FILE}'
  ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
    -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
    --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

  **3. Создайте файл `/etc/conf.d/celery`(vim и nano не хочет сохранять файл без расширения)**

  ```
  touch /etc/conf.d/celery
  ```

  **4. Отройкте файл `/etc/conf.d/celery` и добавьте в него следующее содержимое**

  ```
  vim /etc/conf.d/celery
  ```

  ```
  CELERY_APP="lol_pay"

  CELERY_BIN="/root/Lol-pro/venv/bin/celery"

  CELERYD_NODES="w1"

  CELERYD_MULTI="multi"

  CELERYD_OPTS="--time-limit=300 --concurrency=8"

  CELERYD_PID_FILE="/var/run/celery/%n.pid"

  CELERYD_LOG_FILE="/var/log/celery/%n%I.log"

  CELERYD_LOG_LEVEL="INFO"

  CELERYBEAT_SCHEDULE_FILE="/var/run/celery/celerybeat-schedule"

  CELERYBEAT_PID_FILE="/var/run/celery/beat.pid"

  CELERYBEAT_LOG_FILE="/var/log/celery/beat.log"


  CELERY_FLOWER_URL_PREFIX="flower"

  CELERY_FLOWER_LOG_FILE="/var/log/celery/flower.log"

  CELERY_FLOWER_ADDRESS="127.0.0.1"

  CELERY_FLOWER_PORT="5555"
  ```

  **5. Создайте файл `/etc/tmpfiles.d/celery.conf` со следующим содержимым**

  ```
  vim /etc/tmpfiles.d/celery.conf
  ```

  ```
  d /var/run/celery 0755 lol_pay www-data -
  d /var/log/celery 0755 lol_pay www-data -
  ```

  **6. Примените изменения**

  ```
  sudo systemctl daemon-reload
  ```

  **7. Запустите службу `Celery`**

  ```
  sudo systemctl start celery
  ```

  **8. Включите службу `Celery`**

  ```
  systemctl enable celery.service
  ```

  **9. Проверьте работоспособность `Celery`**

  ```
  sudo systemctl status celery
  ```
  <br/>

<a id="setup-flower_beat"></a>
* **Настройка `Celery flower` и `Celery beat`**

  **1. Создайте файл `/etc/systemd/system/celerybeat.service` со следующим содержимым**

  ```
  vim /etc/systemd/system/celerybeat.service
  ```

  ```
  [Unit]
  Description=Celery Beat Service
  After=network.target

  [Service]
  Type=simple
  User=root
  Group=www-data
  EnvironmentFile=/etc/conf.d/celery
  WorkingDirectory=/root/Lol-pro
  ExecStart=/bin/sh -c '${CELERY_BIN} -A ${CELERY_APP} beat \
    -s ${CELERYBEAT_SCHEDULE_FILE} \
    --pidfile=${CELERYBEAT_PID_FILE} \
    --logfile=${CELERYBEAT_LOG_FILE} \
    --loglevel=${CELERYD_LOG_LEVEL}'
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

  **2. Создайте файл `/etc/systemd/system/celeryflower.service` со следующим содержимым**

  ```
  vim /etc/systemd/system/celeryflower.service
  ```

  ```
  [Unit]
  Description=Flower Celery Service
  After=network.target

  [Service]
  User=root
  Group=www-data
  EnvironmentFile=/etc/conf.d/celery
  WorkingDirectory=/root/Lol-pro
  ExecStart=/bin/sh -c '${CELERY_BIN} -A ${CELERY_APP} flower \
    --url_prefix=${CELERY_FLOWER_URL_PREFIX} --port=${CELERY_FLOWER_PORT} \
    --address=${CELERY_FLOWER_ADDRESS} \
    --log-file-prefix=${CELERY_FLOWER_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL}'
  Restart=on-failure
  Type=simple

  [Install]
  WantedBy=multi-user.target
  ```

  **3. Примените изменения**

  ```
  sudo systemctl daemon-reload
  ```

  **4. Запустите службу `Celery beat`**

  ```
  sudo systemctl start celerybeat
  ```

  **5. Запустите службу `Celery flower`**

  ```
  sudo systemctl start celeryflower
  ```

  **6. Включите службу `Celery beat`**

  ```
  systemctl enable celerybeat.service
  ```

  **7. Включите службу `Celery flower`**

  ```
  systemctl enable celeryflower.service
  ```

  **8. Проверьте работоспособность `Celery beat`**

  ```
  sudo systemctl status celerybeat
  ```

  **9. Проверьте работоспособность `Celery flower`**

  ```
  sudo systemctl status celeryflower
  ```
  <br/>

<a id="setup-nginx"></a>
* **Настройте Nginx для пропуска прокси к Gunicorn**

  **1. Создайте файл `/etc/nginx/sites-available/lol_pay` со следующим содержимым**

  ```
  vim /etc/nginx/sites-available/lol_pay
  ```

  ```
  server {
    listen 80;
    server_name <server_ip>;

    location /static/ {
        root /root/Lol-pro;
    }

    location /media/ {
        root /root/Lol-pro;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
  }
  ```

  **2. В файле `/etc/nginx/nginx.conf` первая строчка должна быть `user root;`**

  **3. Создайте символическую ссылку**

  ```
  sudo ln -s /etc/nginx/sites-available/lol_pay /etc/nginx/sites-enabled
  ```

  **4. Проверьте конфигурацию `nginx`**

  ```
  sudo nginx -t
  ```

  **5. Перезапустите `nginx`**

  ```
  sudo systemctl restart nginx
  ```

  **6. Удалите `8000` порт из входящего трафика**

  ```
  sudo ufw delete allow 8000
  ```

  **7. Разрешите входящий трафик через `firewall` порт `80`**

  ```
  sudo ufw allow 'Nginx Full'
  ```

  **8. Перезапустите `gunicorn`**

  ```
  sudo systemctl restart gunicorn
  ```

  **9. Перезагрузите сервер**

  ```
  sudo shutdown -r now
  ```

  **10. Откройте проект в браузере по адресу**

  ```
  http://<server_ip>/
  ```

  **Если проект успешно отобразился можно идти дальше**
<br/><br/>

<a id="setup-domain"></a>
* **Подключение домена**

  **1. После покупки домена нужно подключить `DNS` на хостинге вашего сервера. Создайте А-запись с привязкой к ip вашего сервера.**

  **2. Измените конфигурацию `nginx`**

  ```
  vim /etc/nginx/sites-available/lol_pay
  ```

  ```
  server {
    listen 80;
    server_name <domain> www.<domain> <server_ip>;

    location /static/ {
        root /root/Lol-pro;
    }

    location /media/ {
        root /root/Lol-pro;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
  }
  ```

  **3. Перезапустите `nginx`**

  ```
  sudo systemctl reload nginx
  ```

  **4. Проверьте конфигурацию `nginx`**

  ```
  sudo nginx -t
  ```

  **5. Добавьте новые доменные имена в `ALLOWED_HOSTS` в файле `settings.py`**

  ```
  vim /root/Lol-pro/lol_pay/settings/base.py
  ```

  ```python

    ALLOWED_HOSTS = ['domain', 'www.domain', 'server_ip']
  ```

  **6. Примените изменения**

  ```
  service gunicorn restart
  ```

  **Теперь может потребоваться некоторое время пока ваш сайт станет доступным на вашем домене**

  **Когда ваш сайт станет доступен на вашем домене - можно идти дальше**
  <br/><br/>

<a id="HTTPS-settings"></a>
* **Настройка `HTTPS`**

  **1. Установите `certbot`**

  ```
  sudo apt install certbot python3-certbot-nginx
  ```

  **2. Проверьте установился ли `certbot`**

  ```
  certbot --version
  ```

  **3. Убедитесь, что конфигурация `nginx` в порядке**

  ```
  sudo nginx -t
  ```

  **4. Удалите `HTTP` порт из входящего трафика**

  ```
  sudo ufw delete allow 'Nginx HTTP'
  ```

  **5. Получите `SSL-сертификат`**

  ```
  sudo certbot --nginx -d <domain> -d www.<domain>
  ```

  **6. Проверьте состояние службы `certbot.timer`**

  ```
  sudo systemctl status certbot.timer
  ```

  **7. Протестируйте процесс обновления**

  ```
  sudo certbot renew --dry-run
  ```

  **8. Обновите конфигурацию `nginx`**

  ```
  vim /etc/nginx/sites-available/lol_pay
  ```

  ```
  server {
    listen 80;

    server_name www.<domain> <domain>;

    return 301 https://$host$request_uri;
  }

  server {
    listen 443 ssl;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;

    server_name www.<domain>;

    return 301 $scheme://<domain>$request_uri;
  }

  server {
    listen 443 ssl;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    server_name <domain>;

    client_max_body_size 20M;

    location /static/ {
        root /root/Lol-pro;
    }

    location /media/ {
        root /root/Lol-pro;
    }

    location / {
        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass http://unix:/run/gunicorn.sock;
    }

    location /ws/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;

        proxy_pass http://127.0.0.1:8001;
      }
  }
  ```

  **9. Обновите конфигурацию `Daphne`**

  ```
  vim /etc/systemd/system/daphne.service
  ```

  ```
  [Unit]
  Description=WebSocket Daphne Service
  After=network.target

  [Service]
  Type=simple
  User=root
  WorkingDirectory=/root/Lol-pro
  ExecStart=/root/Lol-pro/venv/bin/python /root/Lol-pro/venv/bin/daphne -b 127.0.0.1 -p 8001 lol_pay.asgi:application
  Restart=on-failure

  [Install]
  WantedBy=multi-user.target
  ```

  **10. Перезапустите `nginx`**

  ```
  sudo systemctl restart nginx
  ```

  **11. Перезагрузите сервер**

  ```
  sudo shutdown -r now
  ```
  <br/>

<a id="checking-services"></a>
* **Проверка служб**

  **Проверьте следующие службы**

  ```
  sudo systemctl status gunicorn
  ```

  ```
  sudo systemctl status daphne
  ```

  ```
  sudo systemctl status redis
  ```

  ```
  sudo systemctl status celery
  ```

  ```
  sudo systemctl status celeryflower
  ```

  ```
  sudo systemctl status celerybeat
  ```

  ```
  sudo systemctl status nginx
  ```

  ```
  sudo systemctl status certbot.timer
  ```

* **Так же не забудьте настроить Google ReCAPTCHA**
<br/>

* **Настройка парсинга новостей на сайте**

  *Обновление пакетов:*

  ```
  sudo apt update
  ```
  *Установка зависимостей:*

  ```
  sudo apt install curl software-properties-common apt-transport-https ca-certificates gnupg2 -y
  ```
  *Установка Google Chrome*

  ```
  sudo apt install google-chrome-stable -y
  ```

  *Установка необходимых библиотек для работы с браузером в headless-режиме*

  ```
  sudo apt install -y unzip xvfb libxi6 libgconf-2-4
  ```

  *Скачивание и установка ChromeDriver*

  ```
  sudo apt install chromium-chromedriver
  ```


  **Если все работает корректно, тогда посетите ваш сайт по адресу `https://<domain>/` и убедитесь, что все работет как и должно работать.**
 <br/>

  **Спасибо, что уделили время, чтобы познакомиться с моим проектом! Я надеюсь, что он окажется полезным и интересным для вас. Если у вас возникнут вопросы или предложения, не стесняйтесь обращаться ко мне.**
<br/><br/>

# FAQ

* **Команды**
<br/>

  * **Серверные**
  <br/>

    `sudo systemctl status <service_name>` - Посмотреть статус службы<br/>
    `sudo systemctl stop <service_name>` - Остановить службу<br/>
    `sudo systemctl start <service_name>` - Запуск службы<br/>
    `sudo systemctl restart <service_name>` - Перезапуск службы<br/>
    `sudo systemctl disable <service_name>` - Отключить автозапуск службы<br/>
    `sudo journalctl -u <service_name>` - Посмотреть логи службы<br/>
    `sudo systemctl enable <service_name>` - Включить автозапуск службы<br/><br/>

    `sudo systemctl restart gunicorn` - При изменении файлов проекта<br/>
    `sudo systemctl restart daphne` - При изменении файлов связанных в `Websocket`
    <br/>

    `sudo journalctl -u gunicorn` - Посмотреть логи сервера
  <br/>

  * **linux**<br/>

    `rm <path>` - Удалить файл<br/>
    `rmdir <path>` - Удалить директорию<br/>
    `mkdir <path>` - Создать директорию<br/>
    `cd <path>` - Перейти в директорию<br/>
    `cd ..` - Перейти на директорию назад<br/>
    `touch <path>` - Создать файл<br/>
    `echo '<content>' > <path>` - Записать информацию в конец файла<br/>
    `sudo ss -tulpn` - Посмотреть открытые порты<br/>
    `pwd` - Посмотреть в какой директории я сейчас нахожусь<br/>
    `ls <path>` - Посмотреть какие файлы содержит директория<br/>
    `ls -l <path>` - Тоже самое, что и `ls <path>`, но будут показаны доп. параметры файлов<br/>
    `ip a` - Узнать `ip` сервера

    <br/>

  * **VIM**<br/>

    #### Command mode
    `:q` - Выйти из `vim`<br/>
    `:q!` - Выйти из `vim` без изменений<br/>
    `:qw` - Выйти из `vim` с сохранением<br/>
    `:w` - Сохранить файл<br/>
    `v` - Выделение посимвольно<br/>
    `shift+v` - Выделение построчно<br/>
    `y` - Скопировать<br/>
    `p` - Вставить<br/>
    `gg` - Перейти в начало файла<br/>
    `shift+g` - Перейти в конец файла<br/>
    `a` - Начать писать справа от курсора<br/>
    `i` - Начать писать слева от курсора<br/>

    ### Insert mode

    `esc` - Зайти в режим `Command mode`<br/>
