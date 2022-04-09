# Suricate bot
<p align="center" width="100%">
    <img width="50%" src="https://sun9-18.userapi.com/impf/ZFuLrgObN-IVhJvDrVzGdyeQoW2Q0MrpwxVvEQ/OJlZH0hEFQE.jpg?size=736x578&quality=96&sign=b9d25af7303bfff9cf090ba53bb680da&type=album?raw=true">
</p>

## Введение
**Проблема:** 
У нас с девушкой раздельный бюджет (каждый платит за себя, либо делим пополам).
Всех всё устраивает, но в такой модели походы в магазин становятся настоящей мукой.
После каждой покупки продуктов на несколько дней надо сесть и распределить продукты 
на общие, личные того, кто платил, и личные "должника", и записать это в долговой список.

**Решение:** 
После нескольких таких разборов стопки чеков я всё же решил потратить недельку и 
написать Telegram-бота для автоматизации данной задачи.
"Киллер фичей" данного бота я считаю возможность считать список продуктов и дату покупки из QR-кода на чеке.
Но так как парсинг этих данных связан с ФНС, то проект может быть полезен в целом для людей из России.
Именно поэтому README, комментарии и фразы бота на русском.
Проект получился достаточно личным и "семейным", но если вы столкнулись с такой же проблемой, или вам просто хочется посмотреть на него, то приятного просмотра.
Спасибо, что загляну ли в мой репозиторий :)


## Настройка
Создать файл `bot_config.py` с подобным содержанием:
```
INN = "ваш ИНН"
PASSWORD = "пароль от портала ФНС"
CLIENT_SECRET = "с портала ФНС"

TOKEN = "токен бота"
SELECTED_USERS = [123456789, 012345678]  # id пользователей с доступом к боту (9 цифр)
```

## Тесты
В репозитории есть файлы: `test_db.py` и `test_qr_nalog.py`.
При помощи этих файлов вы можете проверить работоспособность мудулей по работе с базой данных и обработкой QR-кодов.

## Установка и запуск
```
docker build -t suricate_bot ./
docker run -d suricate_bot
```
*(-d, --detach:  Run container in background and print container ID)*

# Работа с ботом
## Начало
Приветственное сообщение, которое подсказывает, как работать с ботом.
![start](https://sun9-20.userapi.com/impf/g_BxHi2Q6LqnH9ndumOV7th0ldYYBhLjmBxMLA/lleIm2aDzms.jpg?size=1080x469&quality=96&sign=2a6d1c9782555ce385e6f5a289d548c3&type=album?raw=true)

В нижней панели имеется две кнопки. Одна выводит справку об основных командах.
А вторая быстро выводит результат: кто сколько должен в итоге.
![buttons](https://sun9-80.userapi.com/impf/GRfOwTcINfWu3WlH4p7fXRpMMcsxHS2w2e7o3g/GSTtPTqq97w.jpg?size=1080x1484&quality=96&sign=c43c0360b74a213454cb8c938eba5e9f&type=album?raw=true)

Далее следует добавить пользователей в базу данных (далее БД):
![1payer](https://sun9-1.userapi.com/impf/_ZZEik6mPItreCvec1Z970FJnjxgTYiZLkbXMw/2d9Q0YGtsy0.jpg?size=1080x1510&quality=96&sign=69db95f21cb127231e61e5c3796dd7d6&type=album?raw=true)
И добавим второго:
![2payer](https://sun9-66.userapi.com/impf/DO7mPMNeigv_J6Pfh92vNMJesJnxJl7p0IE9TA/D5_e0wyoEN4.jpg?size=1080x845&quality=96&sign=545e1b1c56e14f8f33112dc89bf2328c&type=album?raw=true)

При попытке добавить третьего вызовется ошибка. Это бот для двух человек
![3payer](https://sun9-78.userapi.com/impf/b721e7sPUftkMA7CyqigCglfYcRYvknI0qu6HQ/UdfdUURMgFk.jpg?size=1080x613&quality=96&sign=65d243bf0ddb01f9b0dce349d305e941&type=album?raw=true)

На этом основная настройка закончена. Теперь вы можете пользоваться ботом в "штатном режиме"!
![payers](https://sun9-25.userapi.com/impf/-XmNRMx8eHhC-59LZihHOhjcfl2ajnAUo1Tz8w/9zBHYHxeduk.jpg?size=1080x1164&quality=96&sign=5e17f8bfc55bed33427ca9fea9a27ff6&type=album?raw=true)

## Ежедневное использование
### Первая покупка c чеком
Для начала можно просто загрузить фото с QR-кодом из чека:
![1check](https://sun9-16.userapi.com/impf/4PC6IYuIaadB4z4kPk-2Wl-iX-jRMD6D-MP20w/gPKCB-dKURw.jpg?size=754x2160&quality=96&sign=779dbd2227b65f62ab8d161742664846&type=album?raw=true)
Бот предложит 3 варианта:
- Если вы ошиблись, то просто нажмите кнопку "Отменить"
- Если вы знаете, что покупали только общие продукты, то просто нажмите "Пополам"
- Если же вы покупали какие-то продукты только для себя любимого, то кнопка "Уточнить" для вас

Воспользуемся последним вариантом. Бот предложит выбрать, кто оплатил покупку.
![1checkPayer](https://sun9-85.userapi.com/impf/EY7EclE75LGqtz4130AD5SmZV-bggSnpqJjfHg/btYyaRose28.jpg?size=1080x575&quality=96&sign=22a755b51b034d77c203ee89fa843332&type=album?raw=true)

А потом вы можете уточнить товары при помощи кнопок, как это описано в сообщении.
![1checkResolve](https://sun9-78.userapi.com/impf/wZuOStQtiuMdgZ_m1eh9idOlvZrfwhpY-JWhVw/iNUgroNODMs.jpg?size=754x2160&quality=96&sign=13d99bbc173dcebb1797355a9976afc1&type=album?raw=true)

В завершении нажимаем "Завершить уточнение"
![1checkResult](https://sun9-51.userapi.com/impf/V9YGzDKQvl0gXC9o7unq6ouJAcUcxHtkJDbVGg/7CYGTgnHH9o.jpg?size=1080x362&quality=96&sign=ee6ca62b6e9850d574c6eac7afe31627&type=album?raw=true)

Проверить нашу покупку в списке долгов можно при помощи команды:
![1checkCost](https://sun9-80.userapi.com/impf/XvsJKySJvz1w74P4aUFGFO7Y-VMumP4tWMNJ9Q/1UYtU0EsUVk.jpg?size=1080x466&quality=96&sign=85e3b8cfd8446faaed118d57f2c0b9be&type=album?raw=true)

### Вторая покупка с чеком
Снова отправляем фото чека
![2check](https://sun9-10.userapi.com/impf/XF9bxWYpzQJxlMGfe44uXch27-IrOUFsA9WH7A/i2AlHrTvmpM.jpg?size=973x2160&quality=96&sign=b9bbc051d4cc2c63b98188f8a9bc4433&type=album?raw=true)

Но в этот раз мы точно знаем, что покупка была общей.
Поэтому нам просто нужно разделить сумму пополам и записать её в базу долгов.
![2checkResolve](https://sun9-45.userapi.com/impf/ITIs9bNoaLAlXhrFWEKO0DsCEiyjJLl6RXQPXA/JXpdGeE63aI.jpg?size=1080x741&quality=96&sign=bcea7dc106225f3581ed842c90204aa2&type=album?raw=true)

Мы видим, что обе наши покупки в базе.
И мы легко можем узнать, кто и сколько должен.
![2checkCost](https://sun9-84.userapi.com/impf/6QEaYDEhg9Yl3VEBOXh4AzPFrXHGEZqhpK01yw/kVlRQ9VNaXs.jpg?size=1080x1006&quality=96&sign=423116b7cfdb7392d13205434f2c1c6a&type=album?raw=true)

### Третья покупка (быстрый текстовый вариант)
Если у вас нет чека (например: автобус, такси и т.д.) или вы просто его выкинули, но помните сумму, и что она общая.
То вы можете просто написать свою покупку в формате "МАГАЗИН - СУММА" ('-' обязательно).
![1custom](https://sun9-80.userapi.com/impf/EqCp83XIcLdpl0UpJfTh3Q1zEE_CHfpWD14jkg/v1_3qpJY0Wk.jpg?size=1080x531&quality=96&sign=bfa7b9acb3da18971e4a8afd40cfd937&type=album?raw=true)

Но, если вы вдруг осознали, что ошиблись с расходом, то можете в любой момент удалить его из БД.
![delCost](https://sun9-49.userapi.com/impf/q1idA3PtiMVHWE0MBpO4MFqnru0ypoWIISPIzQ/KkcKsoRFGw4.jpg?size=1080x1901&quality=96&sign=4b6cb3525c2b01d57809a32ae450ceb2&type=album?raw=true)

## Чистка БД
### Избавляемся от долгов.
Если в какой-то момент вам надоело ходить в должниках, и вы отдали итоговый долг, то можете смело стирать все долги из БД и быть свободным человеком.
![delCosts](https://sun9-81.userapi.com/impf/upKphmzEOpduOFG_QPSCNN2OdubODL4ZyKEDiA/kGCZ4_mx63I.jpg?size=1080x803&quality=96&sign=140dca0bf9774daf4c18393f2b42619a&type=album?raw=true)

Естественно, это действие необратимо. Поэтому будьте внимательны перед тем, как подтверждать его.
После подтверждения все расходы удалятся (пользователи остаются).
![delCostsResult](https://sun9-71.userapi.com/impf/vtf0le-gucxMbGYFmqIbRkpWfU6beRxQxM0Szg/eLIuFZ3U86A.jpg?size=1080x870&quality=96&sign=9575426836768c9508c3730783d14cc0&type=album?raw=true)

### Новая жизнь
Если в вашей жизни начался новый этап (или вам просто надело быть Котиксоном), то в любой момент можно произвести обнуление.
Данная операция очистит всю БД, в том числе и долги с пользователями.
![delDB](https://sun9-32.userapi.com/impf/ZMGQ0JKuRpdIQeTU6Rk_ZKynzsMllBuVR4luAg/l0OUcSQ07o0.jpg?size=1080x901&quality=96&sign=26a90bc55045f2a9f30b795c7c422a5a&type=album?raw=true)

После удаления вы увидите подтверждающее сообщение и можете начать всё с белого листа.
![delDBResult](https://sun9-83.userapi.com/impf/0kznnYm6kMKCrmpAkXDKRSVNSGoYeIm0AA0lXg/c8OLGdvxL-U.jpg?size=1080x245&quality=96&sign=151207670b5c0aadd4ffa5f78d2364df&type=album?raw=true)


# Конец
Спасибо за внимание к моему проекту, а так же за чтение такого большого README.
Хорошего дня!

