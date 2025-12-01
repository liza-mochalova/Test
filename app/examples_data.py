# examples_data.py
"""
Реальные примеры для тестирования API химических реактивов
"""

def get_storage_examples():
    """Примеры мест хранения с реальными названиями"""
    return [
        {
            "name": "Холодильник для кислот",
            "type": "refrigerator",
            "max_capacity": 50,
            "description": "Для хранения кислот классов 2-3 опасности"
        },
        {
            "name": "Шкаф для щелочей и солей", 
            "type": "cabinet",
            "max_capacity": 100,
            "description": "Для хранения щелочей и солей классов 2-3 опасности"
        },
        {
            "name": "Морозильная камера -20°C",
            "type": "freezer",
            "max_capacity": 30,
            "description": "Для термочувствительных реактивов классов 2-3 опасности"
        },
        {
            "name": "Сейф для особо опасных",
            "type": "safe", 
            "max_capacity": 20,
            "description": "ТОЛЬКО для реактивов 1 класса опасности"
        }
    ]

def get_reagent_examples():
    """Реальные химические реактивы с правильным распределением по классам опасности"""
    from datetime import date
    import random
    
    # Будущие даты (следующие 1-2 года)
    future_dates = [
        date(2025, 6, 15),
        date(2025, 8, 20), 
        date(2025, 12, 10),
        date(2026, 3, 30),
        date(2026, 7, 15)
    ]
    
    return [
        # КЛАСС 1 - ТОЛЬКО В СЕЙФЕ
        {
            "name": "Бромистый цианид",
            "formula": "CNBr",
            "cas_number": "5106-68-3",
            "quantity": 500.0,
            "unit": "g",
            "hazard_class": 1,
            "expiry_date": random.choice(future_dates),
            "storage_name": "Сейф для особо опасных",
            "description": "Чрезвычайно токсичное соединение. Класс 1 - только в сейфе!"
        },
        {
            "name": "Нитрит натрия технический",
            "formula": "NaNO₂",
            "cas_number": "7632-00-0",
            "quantity": 1000.0,
            "unit": "g",
            "hazard_class": 1,
            "expiry_date": random.choice(future_dates),
            "storage_name": "Сейф для особо опасных",
            "description": "Сильный окислитель. Класс 1 - только в сейфе!"
        },
        
        # КЛАСС 2 - ХОЛОДИЛЬНИК И ШКАФ
        {
            "name": "Соляная кислота концентрированная",
            "formula": "HCl",
            "cas_number": "7647-01-0",
            "quantity": 2500.0,
            "unit": "ml",
            "hazard_class": 2,
            "expiry_date": random.choice(future_dates),
            "storage_name": "Холодильник для кислот",
            "description": "Концентрированная HCl, 36-38%. Высокоопасная."
        },
        {
            "name": "Гидроксид натрия чистый",
            "formula": "NaOH", 
            "cas_number": "1310-73-2",
            "quantity": 2000.0,
            "unit": "g",
            "hazard_class": 2,
            "expiry_date": random.choice(future_dates),
            "storage_name": "Шкаф для щелочей и солей",
            "description": "Чистый NaOH, гранулы. Высокоопасная щелочь."
        },
        
        # КЛАСС 3 - ШКАФ И МОРОЗИЛЬНИК
        {
            "name": "Ацетон для анализа",
            "formula": "C₃H₆O",
            "cas_number": "67-64-1",
            "quantity": 5000.0,
            "unit": "ml", 
            "hazard_class": 3,
            "expiry_date": random.choice(future_dates),
            "storage_name": "Шкаф для щелочей и солей",
            "description": "Ацетон ч.д.а. Умеренно опасный."
        },
        {
            "name": "Этиловый спирт 96%",
            "formula": "C₂H₅OH",
            "cas_number": "64-17-5",
            "quantity": 3000.0,
            "unit": "ml",
            "hazard_class": 3,
            "expiry_date": random.choice(future_dates), 
            "storage_name": "Морозильная камера -20°C",
            "description": "Этанол 96%. Умеренно опасный."
        }
    ]

def get_validation_test_examples():
    """Примеры для тестирования валидации (должны вызывать ошибки)"""
    from datetime import date
    
    return [
        {
            "name": "❌ ТЕСТ: Класс 1 в шкафу (нарушение правил)",
            "formula": "NaCN",
            "cas_number": "143-33-9",
            "quantity": 100.0,
            "unit": "g",
            "hazard_class": 1,
            "expiry_date": "2025-12-31",
            "storage_name": "Шкаф для щелочей и солей",  # ❌ НЕПРАВИЛЬНО!
            "expected_error": "Класс 1 опасности можно хранить только в сейфе",
            "description": "Попытка разместить цианид натрия (класс 1) в обычном шкафу"
        },
        {
            "name": "❌ ТЕСТ: Прошедшая дата срока годности",
            "formula": "H₂SO₄",
            "cas_number": "7664-93-9",
            "quantity": 1000.0,
            "unit": "ml",
            "hazard_class": 2,
            "expiry_date": "2020-01-01",  # ❌ ПРОШЕДШАЯ ДАТА!
            "storage_name": "Холодильник для кислот",
            "expected_error": "Срок годности не может быть в прошлом",
            "description": "Попытка добавить реактив с истекшим сроком годности"
        },
        {
            "name": "❌ ТЕСТ: Неверный CAS номер",
            "formula": "HCl",
            "cas_number": "123-45-6",  # ❌ НЕВЕРНЫЙ ФОРМАТ!
            "quantity": 500.0,
            "unit": "ml",
            "hazard_class": 2,
            "expiry_date": "2025-12-31",
            "storage_name": "Холодильник для кислот",
            "expected_error": "CAS номер должен быть в формате XXXXX-XX-X",
            "description": "Попытка добавить реактив с неправильным CAS номером"
        },
        {
            "name": "❌ ТЕСТ: Отрицательное количество",
            "formula": "NaOH",
            "cas_number": "1310-73-2",
            "quantity": -50.0,  # ❌ ОТРИЦАТЕЛЬНОЕ!
            "unit": "g",
            "hazard_class": 2,
            "expiry_date": "2025-12-31",
            "storage_name": "Шкаф для щелочей и солей",
            "expected_error": "Количество не может быть отрицательным",
            "description": "Попытка добавить реактив с отрицательным количеством"
        },
        {
            "name": "❌ ТЕСТ: Класс опасности 5 (не существует)",
            "formula": "NaCl",
            "cas_number": "7647-14-5",
            "quantity": 1000.0,
            "unit": "g",
            "hazard_class": 5,  # ❌ НЕСУЩЕСТВУЮЩИЙ КЛАСС!
            "expiry_date": "2025-12-31",
            "storage_name": "Шкаф для щелочей и солей",
            "expected_error": "Класс опасности должен быть от 1 до 4",
            "description": "Попытка добавить реактив с несуществующим классом опасности"
        },
        {
            "name": "❌ ТЕСТ: Пустое название",
            "formula": "H₂O",
            "cas_number": "7732-18-5",
            "quantity": 5000.0,
            "unit": "ml",
            "hazard_class": 4,
            "expiry_date": "2025-12-31",
            "storage_name": "Шкаф для щелочей и солей",
            "expected_error": "Название не может быть пустым",
            "description": "Попытка добавить реактив без названия"
        }
    ]

def print_demo_instructions():
    """Подробная инструкция для тестирования"""
    print("=" * 80)
    print("🧪 ИНСТРУКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ API ХИМИЧЕСКИХ РЕАКТИВОВ")
    print("=" * 80)
    
    print("\n🎯 ПРАВИЛА ХРАНЕНИЯ:")
    print("-" * 50)
    print("• КЛАСС 1 (чрезвычайно опасные) → ТОЛЬКО в СЕЙФЕ")
    print("• КЛАСС 2 (высокоопасные) → Холодильник или Шкаф")  
    print("• КЛАСС 3 (умеренно опасные) → Шкаф или Морозильник")
    print("• КЛАСС 4 (малоопасные) → Любое место хранения")
    print("-" * 50)
    
    print("\n🎯 ШАГ 1: СОЗДАЙТЕ МЕСТА ХРАНЕНИЯ")
    print("-" * 40)
    storages = get_storage_examples()
    for i, storage in enumerate(storages, 1):
        print(f"{i}. {storage['name']}")
        print(f"   Тип: {storage['type']}, Вместимость: {storage['max_capacity']}")
        print(f"   {storage['description']}")
        print()
    
    print("\n🎯 ШАГ 2: ДОБАВЬТЕ РЕАКТИВЫ (используйте НАЗВАНИЯ мест хранения!)")
    print("-" * 60)
    reagents = get_reagent_examples()
    for i, reagent in enumerate(reagents, 1):
        print(f"{i}. {reagent['name']} ({reagent['formula']})")
        print(f"   Класс опасности: {reagent['hazard_class']}")
        print(f"   Место хранения: {reagent['storage_name']}")
        print(f"   Количество: {reagent['quantity']} {reagent['unit']}")
        print(f"   CAS: {reagent['cas_number']}")
        print(f"   Срок годности: {reagent['expiry_date']}")
        print()
    
    print("\n🎯 ШАГ 3: ПРОТЕСТИРУЙТЕ ВАЛИДАЦИЮ (должны быть ошибки!)")
    print("-" * 60)
    validation_tests = get_validation_test_examples()
    for i, test in enumerate(validation_tests, 1):
        print(f"{i}. {test['name']}")
        print(f"   Формула: {test['formula']}, CAS: {test['cas_number']}")
        print(f"   Класс: {test['hazard_class']}, Место: {test['storage_name']}")
        print(f"   Ожидаемая ошибка: {test['expected_error']}")
        print(f"   Описание: {test['description']}")
        print()
    
    print("\n🎯 ШАГ 4: ПРОТЕСТИРУЙТЕ ФУНКЦИОНАЛ")
    print("-" * 40)
    print("1. GET /storage/storage-locations - все места хранения")
    print("2. POST /storage/storage-locations - создать место")
    print("3. POST /reagents - добавить реактив (используйте НАЗВАНИЕ места!)")
    print("4. GET /reagents - все реактивы")
    print("5. GET /reagents/filter/search?hazard_class=1 - реактивы 1 класса")
    print("6. GET /reagents/expiring/soon?days=365 - истекающие через год")
    print("7. POST /reagents/1/write-off?quantity=100 - списание")
    print("8. PUT /reagents/1 - обновление данных")
    
    print("\n🎯 ВАЖНО:")
    print("-" * 30)
    print("• При добавлении реактива указывайте НАЗВАНИЕ места хранения")
    print("• Класс 1 опасности можно хранить ТОЛЬКО в сейфе")
    print("• Все даты срока годности - в будущем")
    print("• Все CAS номера - реальные и валидные")
    print("• Протестируйте валидацию - должны получать понятные ошибки")
    
    print("\n" + "=" * 80)
    print("Откройте http://localhost:8000/docs для тестирования через Swagger UI")
    print("=" * 80)

if __name__ == "__main__":
    print_demo_instructions()