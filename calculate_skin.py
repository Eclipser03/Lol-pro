import json
import random

# Путь к файлу JSON
file_path = 'static/chars/assets/skins2price.json'

# Загрузка данных из файла JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Доступные значения цен
available_prices = [175, 225, 315, 420, 750]

# Заполнение цен случайным образом
for skin, price in data.items():
    if price == 0:  # Заполняем только если цена 0
        data[skin] = random.choice(available_prices)

# Сохранение обновленного JSON с ценами
output_path = 'static/chars/assets/skins2price.json'
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Обновленный файл сохранен в {output_path}")
