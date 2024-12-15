from datetime import datetime, timedelta
from itertools import product


class Driver:
    def __init__(self, driver_type, start_time, shift_duration, route_duration, work_days, rest_days):
        self.driver_type = driver_type
        self.start_time = start_time
        self.shift_duration = shift_duration
        self.route_duration = route_duration
        self.end_time = start_time + shift_duration
        self.work_days_left = work_days
        self.rest_days_left = rest_days

    def generate_schedule(self):
        """
        Генерация расписания для водителя с учетом типа, времени начала, длительности маршрута и обеда на конечной станции.
        """
        current_time = self.start_time
        self.schedule = []

        if self.driver_type == 1:
            lunch_interval_start = datetime.combine(self.start_time.date(), datetime.min.time()) + timedelta(hours=13)
            lunch_interval_end = lunch_interval_start + timedelta(hours=2)

            while current_time < self.end_time:
                arrival_time = current_time + self.route_duration

                if lunch_interval_start <= arrival_time <= lunch_interval_end:
                    self.schedule.append((arrival_time, "Перерыв на обед на конечной станции"))
                    current_time = arrival_time + timedelta(hours=1)
                else:
                    self.schedule.append((current_time, "Работа"))
                    current_time = arrival_time

            self.schedule.append((self.end_time, "Пересменка (15 минут)"))

        elif self.driver_type == 2:
            while current_time < self.end_time:
                self.schedule.append((current_time, "Работа"))
                current_time += self.route_duration
                self.schedule.append((current_time, "Перерыв (10 минут)"))
                current_time += timedelta(minutes=10)

            self.schedule.append((self.end_time, "Пересменка (15 минут)"))

        return self.schedule

    def update_counters(self):
        """
        Уменьшает счетчики рабочих и выходных дней.
        Если рабочие дни закончились, переходит к выходным.
        Если выходные закончились, сбрасывает оба счетчика.
        """
        if self.work_days_left > 0:
            self.work_days_left -= 1
        elif self.rest_days_left > 0:
            self.rest_days_left -= 1
        else:
            if self.driver_type == 1:
                self.work_days_left = 5
                self.rest_days_left = 2
            elif self.driver_type == 2:
                self.work_days_left = 1
                self.rest_days_left = 2

    def can_work_today(self):
        """
        Проверяет, может ли водитель работать сегодня.
        """
        return self.work_days_left > 0


def generate_all_combinations(total_drivers, route_duration):
    """
    Вычисляет приспособленность расписания, минимизируя время простоев
    и добавляя штраф за некорректное время начала обеда для водителей первого типа.

    :param total_drivers: Количество водителей.
    :param route_duration: Длительность маршрута.
    :return: Список всех комбинаций расписаний.
    """
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    all_combinations = []

    for class1_count in range(total_drivers + 1):
        class2_count = total_drivers - class1_count

        class1_schedules = []
        for i in range(1, class1_count + 1):
            driver_schedules = []
            for hour in range(6, 10):
                for minute in range(0, 70, 10):
                    start_time = base_date + timedelta(hours=hour, minutes=minute)
                    driver = Driver(
                        driver_type=1,
                        start_time=start_time,
                        shift_duration=timedelta(hours=9),
                        route_duration=route_duration,
                        work_days=5,
                        rest_days=2,
                    )
                    driver_schedules.append((driver, f"Водитель 1-{i}", driver.generate_schedule()))
            class1_schedules.append(driver_schedules)

        class2_schedules = []
        for j in range(1, class2_count + 1):
            driver_schedules = []
            for hour in range(0, 24):
                for minute in range(0, 70, 10):
                    start_time = base_date + timedelta(hours=hour, minutes=minute)
                    driver = Driver(
                        driver_type=2,
                        start_time=start_time,
                        shift_duration=timedelta(hours=12),
                        route_duration=route_duration,
                        work_days=1,
                        rest_days=2,
                    )
                    driver_schedules.append((driver, f"Водитель 2-{j}", driver.generate_schedule()))
            class2_schedules.append(driver_schedules)

        all_schedules = list(product(*class1_schedules, *class2_schedules))
        for schedule_combination in all_schedules:
            schedule_dict = {(driver_name, driver_class): schedule for driver_class, driver_name, schedule in schedule_combination}
            all_combinations.append(schedule_dict)

    return all_combinations


def filter_schedules_with_overlaps(schedule_dict, max_overlaps):
    """
    Отбраковывает расписания, где n или больше пересечений между расписаниями разных водителей.

    :param schedule_dict: Словарь расписаний (ключ — водитель, значение — список событий [(время, событие)]).
    :param max_overlaps: Максимально допустимое число пересечений между расписаниями.
    :return: True, если расписание допустимо, False — если отбраковывается.
    """
    def intervals_overlap(interval1, interval2):
        return interval1[0] < interval2[1] and interval2[0] < interval1[1]

    driver_intervals = {}
    for driver, schedule in schedule_dict.items():
        intervals = []
        for i in range(len(schedule) - 1):
            if schedule[i][1] == "Работа":
                intervals.append((schedule[i][0], schedule[i + 1][0]))
        driver_intervals[driver] = intervals

    overlap_count = 0
    drivers = list(driver_intervals.keys())
    for i in range(len(drivers)):
        for j in range(i + 1, len(drivers)):
            intervals1 = driver_intervals[drivers[i]]
            intervals2 = driver_intervals[drivers[j]]
            for interval1 in intervals1:
                for interval2 in intervals2:
                    if intervals_overlap(interval1, interval2):
                        overlap_count += 1
                        if overlap_count >= max_overlaps:
                            return False

    return True


def evaluate_schedule(schedule_dict):
    """
    Оценить расписание на основе минимизации времени простоя между сменами.
    Возвращает суммарное время простоя (чем меньше, тем лучше).

    :param schedule_dict: Расписание водителей.
    :return: Время простоя расписания.
    """
    idle_time = 0
    all_times = []

    for driver_schedule in schedule_dict.values():
        for time, _ in driver_schedule:
            all_times.append(time)

    all_times = sorted(all_times)

    for i in range(len(all_times) - 1):
        idle_time += (all_times[i + 1] - all_times[i]).total_seconds()

    return idle_time


def find_best_schedule(total_drivers, number_of_buses, route_duration):
    """
    Найти лучшее расписание на основе заданного числа водителей, автобусов и длительности маршрута.

    :param total_drivers: Количество водителей.
    :param number_of_buses: Количество дней для дублирования расписания.
    :param route_duration: Длительность маршрута.
    :return: Лучшее расписание и его время простоя.
    """
    best_schedule = None
    best_idle_time = float('inf')

    all_combinations = generate_all_combinations(total_drivers, route_duration)

    valid = []
    for schedule in all_combinations:
        if filter_schedules_with_overlaps(schedule, number_of_buses):
            valid.append(schedule)

    for idx, schedule_dict in enumerate(valid, start=1):
        idle_time = evaluate_schedule(schedule_dict)
        #print(f"Комбинация {idx}: Простои — {idle_time} секунд")

        if idle_time < best_idle_time:
            best_idle_time = idle_time
            best_schedule = schedule_dict

    return best_schedule, best_idle_time


def duplicate_brute_schedules(driver_schedules, n_days):
    """
    Дублирует расписания водителей на n дней с учётом выходных.

    :param driver_schedules: Список кортежей (водитель, расписание).
    :param n_days: Количество дней для дублирования расписания.
    :return: Новый список расписаний на n дней.
    """
    extended_schedules = []

    for day in range(n_days):
        for driver_name, schedule in driver_schedules.items():
            type_driver = driver_name[0]
            driver = driver_name[1]
            if driver.can_work_today():

                new_schedule = []
                for shift in schedule:
                    start_time = shift[0]
                    job = shift[1]

                    new_shift = (start_time + timedelta(days=day + 1), job)

                    new_schedule.append(new_shift)

                extended_schedules.append((driver, type_driver, new_schedule))

                driver.update_counters()

    return extended_schedules
