from datetime import timedelta
from save_funcs import save_brute_schedule_to_excel, save_genetic_schedule_to_excel
from brute_force import find_best_schedule, duplicate_brute_schedules
from genetic import genetic_algorithm, duplicate_genetic_schedules


def main():
    while True:
        print("Вас приветствует программа по генерации расписания для водителей автобусов!")
        print("Выберите алгоритм для запуска:")
        print("1. Генетический алгоритм")
        print("2. Алгоритм грубой силы")
        print("0. Выход")

        choice = input("Введите номер алгоритма (1 или 2), или 0 для выхода: ")

        if choice == "1":
            while True:
                print("\nМеню генетического:")
                print("0. Вернуться в главное меню")
                number_of_drivers = input("Введите кол-во водителей: ")
                if number_of_drivers == "0":
                    break
                try:
                    number_of_drivers = int(number_of_drivers)
                    break
                except ValueError:
                    print("Ошибка: Кол-во водителей должно быть целым числом. Попробуйте снова.")

            if number_of_drivers == "0":
                continue

            while True:
                print("\nМеню генетического алгоритма:")
                print("0. Вернуться в главное меню")
                number_of_buses = input("Введите кол-во автобусов: ")
                if number_of_buses == "0":
                    break
                try:
                    number_of_buses = int(number_of_buses)
                    break
                except ValueError:
                    print("Ошибка: Кол-во автобусов должно быть целым числом. Попробуйте снова.")

            if number_of_buses == "0":
                continue

            while True:
                print("\nМеню генетического алгоритма:")
                print("0. Вернуться в главное меню")
                route_duration = input("Введите длительность маршрута (в часах): ")
                if route_duration == "0":
                    break
                try:
                    route_duration = float(route_duration)
                    break
                except ValueError:
                    print("Ошибка: Длительность маршрута должна быть числом. Попробуйте снова.")

            if route_duration == "0":
                continue

            while True:
                print("\nМеню генетического алгоритма:")
                print("0. Вернуться в главное меню")
                num_days = input("Введите кол-во дней расписания: ")
                if num_days == "0":
                    break
                try:
                    num_days = int(num_days)
                    break
                except ValueError:
                    print("Ошибка: Кол-во дней должно быть целым числом. Попробуйте снова.")

            if num_days == "0":
                continue

            try:
                schedule_list = genetic_algorithm(number_of_drivers, number_of_buses, route_duration)
                for schedule in schedule_list:
                    if schedule['type'] == 1:
                        print(f"{schedule['driver_id']}-{schedule['type']}")
                        print(f"Начало смены: {schedule['start_time']}")
                        print(f"Начало обеда: {schedule['lunch_start']}")
                        print(f"Конец обеда: {schedule['lunch_end']}")
                        print(f"Конец смены: {schedule['end_time']}")
                        print()
                    else:
                        print(f"{schedule['driver_id']}-{schedule['type']}")
                        print(f"Начало смены: {schedule['start_time']}")
                        print(f"Конец смены: {schedule['end_time']}")
                        print("Перерывы:")
                        for lunch_break in schedule['breaks']:
                            for key in lunch_break.keys():
                                if key == 'break_start':
                                    print(f"Начало перерыва: {lunch_break['break_start']}")
                                else:
                                    print(f"Конец перерыва: {lunch_break['break_end']}")
                        print()

                    if num_days == 1:
                        full_schedule = schedule_list
                    else:
                        full_schedule = schedule_list + duplicate_genetic_schedules(schedule_list, num_days-1)
                    save_genetic_schedule_to_excel(full_schedule, "genetic_schedule.xlsx")

                while True:
                    print("Выберите действие:")
                    print("1. Вернуться в главное меню")
                    print("2. Выйти из программы")
                    choice = input("Введите 1 или 2: ")

                    if choice == "1":
                        break
                    elif choice == "2":
                        print("Выход из программы...")
                        exit()
                    else:
                        print("Неверный выбор. Пожалуйста, введите 1 или 2.")
            except AttributeError:
                print(
                    "Для таких параметров оптимальное расписание не найдено. Пожалуйста, вернитесь в главное меню и "
                    "попробуйте снова.")
                continue

            continue
        elif choice == "2":
            while True:
                print("\nМеню алгоритма грубой силы:")
                print("0. Вернуться в главное меню")
                number_of_drivers = input("Введите кол-во водителей: ")
                if number_of_drivers == "0":
                    break
                try:
                    number_of_drivers = int(number_of_drivers)
                    break
                except ValueError:
                    print("Ошибка: Кол-во водителей должно быть целым числом. Попробуйте снова.")

            if number_of_drivers == "0":
                continue

            while True:
                print("\nМеню алгоритма грубой силы:")
                print("0. Вернуться в главное меню")
                number_of_buses = input("Введите кол-во автобусов: ")
                if number_of_buses == "0":
                    break
                try:
                    number_of_buses = int(number_of_buses)
                    break
                except ValueError:
                    print("Ошибка: Кол-во автобусов должно быть целым числом. Попробуйте снова.")

            if number_of_buses == "0":
                continue

            while True:
                print("\nМеню алгоритма грубой силы:")
                print("0. Вернуться в главное меню")
                route_duration = input("Введите длительность маршрута (в часах): ")
                if route_duration == "0":
                    break
                try:
                    route_duration = timedelta(hours=float(route_duration))
                    break
                except ValueError:
                    print("Ошибка: Длительность маршрута должна быть числом. Попробуйте снова.")

            if route_duration == "0":
                continue

            while True:
                print("\nМеню алгоритма грубой силы:")
                print("0. Вернуться в главное меню")
                num_days = input("Введите кол-во дней расписания: ")
                if num_days == "0":
                    break
                try:
                    num_days = int(num_days)
                    break
                except ValueError:
                    print("Ошибка: Кол-во дней должно быть целым числом. Попробуйте снова.")

            if num_days == "0":
                continue

            try:
                best_schedule, best_idle_time = find_best_schedule(number_of_drivers, number_of_buses, route_duration)
                print(f"\nЛучшее расписание с минимальным временем простоя ({best_idle_time} секунд): ")
                for driver_name, schedule in best_schedule.items():
                    print(f"{driver_name[0]}: ")
                    for time, event in schedule:
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {event}")
                    print()

                if num_days == 1:
                    full_schedule = list(best_schedule)
                else:
                    full_schedule = list(best_schedule) + duplicate_brute_schedules(best_schedule, num_days-1)
                save_brute_schedule_to_excel(full_schedule, "brute_schedule.xlsx")

                while True:
                    print("Выберите действие:")
                    print("1. Вернуться в главное меню")
                    print("2. Выйти из программы")
                    action_choice = input("Введите 1 или 2: ")

                    if action_choice == "1":
                        break
                    elif action_choice == "2":
                        print("Выход из программы...")
                        exit()
                    else:
                        print("Неверный выбор. Пожалуйста, введите 1 или 2.")
            except AttributeError:
                print(
                    "Для таких параметров оптимальное расписание не найдено. Пожалуйста, вернитесь в главное меню и "
                    "попробуйте снова.")
                continue

        elif choice == "0":
            print("Выход из программы...")
            exit()

        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 0 для выхода.")


if __name__ == "__main__":
    main()
