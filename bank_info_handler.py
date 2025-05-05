import json
import os

def save_bank_info_to_json(bank_info, filename='bank_info.json'):
    if not bank_info:
        print("Нет информации о банке для сохранения.")
        return
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # Если файл пустой или содержит некорректный JSON, начинаем с пустого словаря
                data = {}
    else:
        data = {}

    # Используем БИК как ключ, если доступен, иначе используем название
    bank_identifier = bank_info.get('bic', bank_info.get('name', 'Неизвестный банк'))

    # Сохраняем информацию о банке под его идентификатором
    data[bank_identifier] = bank_info

    # Записываем обновленные данные в файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Информация о банке '{bank_identifier}' успешно сохранена в {filename}.")
