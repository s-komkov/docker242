# Docker Compose. Домашнее задание

В качестве основы для домашнего задания использовано приложение на Python, которое подключается к кластеру PostgreSQL, проверяет наличие базы данных и таблицы, и при необходимости создает их. Затем приложение заполняет таблицу данными в соответствии с заданными условиями.

Исходный код приложения и все необходимые файлы для создания контейнера с этим приложением находятся в каталоге `dataset-generator`

## Описание

Приложение выполняет следующие действия:

1. Подключается к кластеру PostgreSQL к базе данных "postgres".
2. Проверяет наличие указанной в переменной окружения `POSTGRES_DATABASE` базы данных, и при отсутствии создает ее.
3. Переключается на созданную базу данных.
4. Проверяет наличие таблицы "data", и при отсутствии создает ее с заданными атрибутами.
5. Проверяет наличие данных в таблице "data".
6. Если таблица пуста, начинает заполнение ее данными в формате:
```sql
id SERIAL PRIMARY KEY,
timestamp TIMESTAMP,
record VARCHAR(250)
```
7. Если в таблице есть данные, считывает последнюю строку и продолжает заполнение таблицы начиная с последней добавленной строки.
8. После достижения значения количества записей, указанного в переменной окружения `MAX_ROWS`, начинает запись сначала таблицы.

## Задание

Необходимо написать docker-compose.yml файл для запуска контейнера приложения `dataset-generator` совместно с контейнером с `PostgreSQL`
на основе базового образа **postgres:14.7-alpine**. 

**ИЗМЕНЯТЬ ИСХОДНЫЙ КОД ПРИЛОЖЕНИЯ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО!**

## Дополнительные требования
- Перезапуск контейнеров происходит автоматически в случае завершения их работы из-за ошибки
- Проект использует собственную сеть для взаимодействия контейнеров

## Критерии оценки

### **+**
Оба контейнера запускаются, производится создание базы данных, таблицы и запись в таблицу

### **++** 
Тоже что и в первом пункте, только для контейнера с `PostgreSQL` добавлени правильный `healthcheck`. Запуск контейнера с приложением `dataset-generator` производится только после полного запуска контейнера с `PostgreSQL`.

### **+++** 
Правильно выполнены первые два пункта и для контейнера `PostgreSQL` учтена возможность сохранения данных при перезагрузке, т.е. остаются все записи в таблице
после перезапуска контейнера или остановки всего приложения с помощью команды `docker compose down`. 
**Примечание:** На уровне приложения `dataset-generator` гарантируется возможность продолжения записи с последней добавленой строки.

## Настройки

Настройки работы приложения `dataset-generator` производятся через переменные окружения. Переменные представлены со значениями по умолчанию:

| **Название переменной** | **Значение по умолчанию** | **Описание**                                                 |
|-------------------------|---------------------------|--------------------------------------------------------------|
| `POSTGRES_USER`         | postgres                  | Пользователь для подключения к PostgreSQL                    |
| `POSTGRES_PASSWORD`     | postgres                  | Пароль для подключения к PostgreSQL                          |
| `POSTGRES_DATABASE`     | homework                  | Название базы данных, для добавления данных                  |
| `POSTGRES_HOST`         | 127.0.0.1                 | IP-адрес или hostname PostgreSQL                             |
| `POSTGRES_PORT`         | 5432                      | Порт для подключения к PostgreSQL                            |
| `MAX_ROWS`*             | 300                       | Максимальное количество строк для добавления в таблицу       |
| `DATA_INSERTION_DELAY`* | 5                         | Таймаут задержки в секундах перед добавлением новой строки   |

Параметры отмеченные звездочкой **\*** доступны для изменения только в рамках тестирования. В итоговом файле убедительная просьба не использовать их 
или задать значения по умолчанию


### 
---
### 

# Краткое руководство по Docker-Compose

Это краткое руководство по использованию Docker-Compose.

## Содержание

- [Краткое руководство по Docker-Compose](#краткое-руководство-по-docker-compose)
  - [Содержание](#содержание)
  - [services](#services)
  - [image](#image)
  - [build](#build)
  - [ports](#ports)
  - [healthcheck](#healthcheck)
  - [depends_on](#depends_on)
  - [container_name](#container_name)
  - [environment](#environment)
  - [restart](#restart)
  - [command](#command)
  - [volumes](#volumes)
    - [Bind Mounting](#bind-mounting)
    - [Volume Mounting](#volume-mounting)
    - [Совместный способ использования Volume и Bind](#совместный-способ-использования-volume-и-bind)
  - [networks](#networks)

## services

Файл docker-compose обычно начинается с указания версии и перечисления сервисов.

`version` определяет, какую версию docker-compose следует использовать.
`services` - это просто список контейнеров, которые вы хотите запустить.

В данном случае у нас есть три контейнера, которыми мы хотим управлять:

1. Database
1. Redis
1. App

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
```

### image  
[[наверх]](#содержание)

Вы можете указать, с какого базового образа следует запускать ваши сервисы.

```yaml
version: "3.8"

services:
  database:
    image: postgres:9.4
  redis:
    image: redis:alpine
  app:
    image: my-app
```

### build
[[наверх]](#содержание)

Если у вас есть Dockerfile из которго вы хотите собрать образ, а затем использовать его, вы также можете указать это в docker-compose.yml.
С точкой вы фактически говорите, что контекст сборки и `Dockerfile` находится в том же каталоге, что и файл docker-compose.yml. 
Вы также можете дополнительно указать директиву `image`. В этом случае, если Dockerfile будет не найден, docker-compose будет использовать образ указанный в `image`.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    build: .
    image: my-app
```

### ports
[[наверх]](#содержание)

Вы можете открывать порты внутри контейнера и привязать их к портам хоста. Синтаксис `HostPort:ContainerPort`, например, `9090:8080` - порт 8080 в контейнере теперь отображается на порт 9090 на хосте.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
```

### healthcheck
[[наверх]](#содержание)

Настройте проверку, чтобы определить, находятся ли контейнеры в статусе «healthy». Проверка необходима для того, чтобы убедиться что службы 
внутри контейнера запущены корректно и готовы к работе, т.к. не все службы сразу активны вместе с запуском контейнера.
Проверка представляет собой команду, выполняемую внутри контейнера и отслеживанием кода ее завершения. Допустимые значения кода завершения:

 - 0: успешно - контейнер успешно запущен и сервис готов к работе
 - 1: ошибка - сервис внутри контейнера работает некорректно.

 Параметры для `healthcheck`:
 - `test` - команда для отслеживания состояния контейнера. Должна возвращать только 0 или 1. Может быть задана в различных эквивалентных формах:

```yaml
test: ["CMD", "curl", "-f", "http://localhost"] # эквивалентно exec форме
test: ["CMD-SHELL", "curl -f http://localhost"] # эквивалентно shell форме, просто передается в форме списка
test: curl -f https://localhost                 # эквивалентно shell форме
```

 - `interval` - периодичность запуска проверок командой `test`
 - `timeout` - таймаут выполнения команды `test`, после которого проверка считается проваленой
 - `retries` - максимальное количество неудачных попыток
 - `start_period` - обеспечивает время инициализации для контейнеров. Ошибки команды `test` в течение этого периода не будет засчитываться в максимальное количество повторных попыток `retries`

```yaml
version: "3.8"
services:
  rabbitmq:
    image: rabbitmq:3.10.7-management
    restart: always
    # Healthcheck для проверки доступности RabbitMQ через HTTP запрос к Management Interface
    # Проверка выполняется внутри контейнера RabbitMQ
    healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:15672"]
        interval: 10s
        timeout: 5s
        retries: 10
```

### depends_on
[[наверх]](#содержание)

Если у вас есть два или более контейнеров, для которых важен порядок запуска, вы можете использовать `depends_on` для указания того, что один сервис зависит от другого, а также указывать дополнительные условия в строке `conditions`.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
```

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    depends_on:
      redis:
        condition: service_healthy
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
```

### container_name
[[наверх]](#содержание)

Вы также можете указать пользовательское имя для вашего контейнера.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
    container_name: my-web-container
```

### hostname
[[наверх]](#содержание)

Вы можете указать `hostname` для вашего контейнера и создать таким образом DNS запись внутри вашей сети контейнеров.
Таким образом вы сможете обращать к контейнеру используя `hostname` вместо адреса.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
    container_name: my-web-container
    hostname: app-local
```


### environment
[[наверх]](#содержание)

Вы также можете указать переменные окружения непосредственно в разделе `environment` или через файл .env в разделе `env_file`. 
Эти два способа можно комбинировать.

```yaml
version: "3.8"

services:
  database:
    build: ${PATH_TO_DOCKERFILE}
  redis:
    image: "redis:${TAG}"
  app:
    env_file:
      - credentials.env
    environment:
      - DEVELOPMENT=1
      - EDITOR=vim
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
    container_name: my-web-container
```
### restart
[[наверх]](#содержание)

 Определяет поведние **docker** при завершении работы контейнера:

-  `no`: поведение по умолчанию. Контейнер не перезапускается ни при каких обстоятельствах;

- `always`: Контейнер будет перезапускаться ВСЕГДА, до тех пор пока не будет удален. Контейнер также будет перезапущен при перезапуске хоста, если служба **dockerd** активна при запуске;

- `on-failure[:max-retries]`: Контейнер будет перезапущен при завершении его работы, если код выхода не равен нулю. Количество попыток перезапуска может ограничиваться указанием числа через двоеточие `on-failure:3`;

- `unless-stopped`: Контейнер будет перезапускаться при завершении его работы, вне зависимости от кода выхода, до тех пор пока контейнер не будет остановлен или удален.

```yaml
version: "3.8"

services:
  database:
  redis:
  app:
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
    container_name: my-web-container
    hostname: app-local
    restart: always
```


### command
[[наверх]](#содержание)

Переопределите команду внутри контейнера. Поддерживается синтаксис строки или списка. При этом первый элемент списка будет непосредственно командой, а остальные ее аргументами

```yaml
version: "3.8"

services:
  database:
    build: ${PATH_TO_DOCKERFILE}
    command: ["bundle", "exec", "thin", "-p", "3000"]

  redis:
    image: "redis:${TAG}"
  app:
    environment:
      - DEVELOPMENT=1
      - EDITOR=vim
    depends_on:
      - redis
    ports:
      - 9090:8080
      - 5001:80
      - 5858:5858
    build: .
    image: my-app
    container_name: my-web-container
    command: bundle exec thin -p 3000
```

## volumes
[[наверх]](#содержание)

В Docker Compose вы можете создавать тома и точки монтирования для контейнера.

Способы монтирования:
- Bind Mounting: монтирует директорию на вашем хосте.
- Volume Mounting: создает и монтирует том, созданный Docker (docker-volume).
- Bind и Volume Mix: можно также использовать совместно volume-mounting и bind-mounting.

### Bind Mounting
[[наверх]](#содержание)

Для bind-mounting вам не нужно создавать новый том. Вам нужно просто указать полный путь к директории, которую вы хотите примонтировать. Синтаксис `Source:Target`, где `Source` - это локальная директория, которую вы хотите примонтировать в директорию `Target` внутри контейнера.

#### Краткий синтаксис

```yaml
version: "3.8"

services:
  database:
    volumes:
      - ~/Document/databases:/var/lib/mysql/data
  redis:
  app:
```

#### Длинный синтаксис
Длинный синтаксис более читаем. Вы указываете тип, источник и цель.

```yaml
version: "3.8"

services:
  database:
    volumes:
      - type: bind
        source: ~/Documents/databases
        target: /var/lib/mysql/data
  redis:
  app:
```

### Volume Mounting
[[наверх]](#содержание)

Мы создадим docker-volume с названием db-data и примонтируем его в контейнер по указанному пути. Физически, созданный том находится в `/var/lib/docker/volumes/db-data/`. Синтаксис похож на bind-mounting `VolumeName:Target`, но вместо пути к каталогу, указывается название docker-volume, обьявленное в директиве `volumes` (данная директива должна находится на одном уровне с `services`).

#### Краткий синтаксис

```yaml
version: "3.8"

services:
  database:
    volumes:
      - db-data:/var/lib/mysql/data
  redis:
  app:

volumes:
  db-data:
```

#### Длинный синтаксис
`no-copy:` флаг для отключения копирования данных из контейнера при создании тома.

```yaml
version: "3.8"

services:
  database:
    volumes:
      - type: volume
        source: db-data
        target: /var/lib/mysql/data
  volume:
    no-copy: true
  redis:
  app:

volumes:
  db-data:
```

### Совместный способ использования Volume и Bind
[[наверх]](#содержание)

Вы также можете использовать совместно volume-mounting и bind-mounting.

#### Краткий синтаксис

```yaml
version: "3.8"

services:
  database:
    volumes:
      - db-data:/var/lib/mysql/data
      - ~/Document/databases:/var/lib/mysql/data
  redis:
  app:

volumes:
  db-data:
```

#### Длинный синтаксис

```yaml
version: "3.8"

services:
  database:
    volumes:
      - type: volume
        source: db-data
        target: /var/lib/mysql/data
        volume:
          no-copy: true
      - type: bind
        source: ~/Documents/databases
        target: /var/lib/mysql/data
  redis:
  app:

volumes:
  db-data:
```

## networks
[[наверх]](#содержание)

По умолчанию контейнеры Docker работают в сети `default`(bridge). Однако вы можете создавать свои собственные сети. Сети создаются так же как и сервисы и тома, а затем каждому сервису присваивается сеть.

В нашем случае мы создали две новые сети `front_end` и `back_end` и назначили `database` сети `back_end`, а `redis` - сети `front_end`.

```yaml
version: "3.8"

services:
  database:
    networks:
      - back_end
  redis:
    networks:
      - front_end
  server:
    networks:
      - front_end
      - back_end
  app:
    networks: [front_end, back_end]

networks:
  front_end:
    ipam:
      driver: default # он же bridge
      config:
      - subnet: 10.28.28.0/24
        gateway: 10.28.28.1
  back_end:
    ipam:
      driver: default
      config:
      - subnet: 10.28.27.0/24
        gateway: 10.28.27.1
```