"""
Файл для демонстрации работы с БД.
"""
import db.dbms as db
from tools import get_now_formatted


db.delete_db()

#%% Добавляем плательщиков.
db.add_payer('Владимир')
db.add_payer('Дарья')


#%% Добавим расход в виде словаря.
cost = {'дата': get_now_formatted(),
        'плательщик': 'Владимир',
        'сумма': 1550,
        'магазин': 'Магнит'}
db.add_cost(cost)


#%% Вывод всех плательщиков.
print('Все плательщики:')
for payer in db.all_payers():
    print(payer)


#%% Итоговый вывод.
print('\n' + db.total_credit())


#%%
cost = {'дата': get_now_formatted(),
        'плательщик': 'Дарья',
        'сумма': 782,
        'магазин': 'Лента'}
db.add_cost(cost)

print('\n' + db.total_credit())


#%%
print('\nВсе расходы:')
for cost in db.all_costs():
    print(cost)
