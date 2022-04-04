FROM python:3.8

# Копируем requirements.txt в /app/
# Обновляем apt-get
# Устанавливаем дополнительно libzbar-dev для pyzbar пакета (qr-коды)
# Устанавливаем все пакеты из requirements.txt
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y build-essential libzbar-dev && \
    pip install --requirement /app/requirements.txt

# Копируем все файлы в /app/
COPY . /app/

# Переходим в /app/ и запускаем бота
WORKDIR /app
CMD python bot.py
