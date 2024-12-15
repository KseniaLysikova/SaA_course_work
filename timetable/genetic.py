import random
import copy
from datetime import datetime, timedelta


class Driver:
    def __init__(self, driver_type, start_time, end_time, work_days, rest_days):
        self.driver_type = driver_type
        self.start_time = start_time
        self.end_time = end_time
        self.work_days_left = work_days
        self.rest_days_left = rest_days

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


def initialize_population(size, total_drivers, route_duration):
    """
    Генерирует популяцию расписаний для случайно распределённых типов водителей с использованием только текущей даты.

    :param size: Размер популяции.
    :param total_drivers: Общее количество водителей.
    :param route_duration: Длительность маршрута.
    :return: Список расписаний.
    """
    population = []
    today_date = datetime.today().date()
    today = datetime.combine(today_date, datetime.min.time())

    for _ in range(size):
        schedule = []

        drivers_type1 = []
        drivers_type2 = []

        for driver_id in range(1, total_drivers + 1):
            if random.random() < 0.5:
                drivers_type1.append(f"Driver-{driver_id}")
            else:
                drivers_type2.append(f"Driver-{driver_id}")

        for driver in drivers_type1:
            start_hour = random.randint(6, 10)
            start_time = today + timedelta(hours=start_hour)
            end_time = start_time

            count = 0
            while count != round(9 / route_duration):
                end_time += timedelta(hours=route_duration)
                count += 1

            lunch_start_hour = random.randint(13, 14)
            lunch_start_time = today + timedelta(hours=lunch_start_hour)
            lunch_end_time = lunch_start_time + timedelta(hours=1)

            schedule.append({
                "driver": Driver(driver_type=1,
                                 start_time=start_time,
                                 end_time=end_time,
                                 work_days=5,
                                 rest_days=2),
                "driver_id": driver,
                "type": 1,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "lunch_start": lunch_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "lunch_end": lunch_end_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        for driver in drivers_type2:
            start_hour = random.randint(0, 23)
            start_time = today + timedelta(hours=start_hour)
            end_time = start_time

            count = 0
            while count != round(12 / route_duration):
                end_time += timedelta(hours=route_duration)
                count += 1

            breaks = []
            current_time = start_time
            while current_time + timedelta(hours=route_duration) < end_time:
                break_start = current_time + timedelta(hours=route_duration)
                break_end = break_start + timedelta(minutes=10)
                breaks.append({
                    "break_start": break_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "break_end": break_end.strftime("%Y-%m-%d %H:%M:%S")
                })
                current_time += timedelta(hours=route_duration)

            schedule.append({
                "driver": Driver(driver_type=2,
                                 start_time=start_time,
                                 end_time=end_time,
                                 work_days=1,
                                 rest_days=2),
                "driver_id": driver,
                "type": 2,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "breaks": breaks
            })

        population.append(schedule)

    return population


def calculate_fitness(schedule, number_of_buses, route_duration_hours):
    """
    Вычисляет приспособленность расписания, минимизируя время простоев
    и добавляя штраф за некорректное время начала обеда для водителей первого типа.

    :param schedule: Список смен для каждого автобуса.
    :param number_of_buses: Количество используемых автобусов
    :param route_duration_hours: длительность маршрута в часах.
    :return: Значение приспособленности (чем меньше, тем лучше).
    """
    today_date = datetime.today().date()
    today = datetime.combine(today_date, datetime.min.time())
    total_idle_time = 0
    penalty = 0

    intervals = []
    for shift in schedule:
        start_time = datetime.strptime(shift['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(shift['end_time'], "%Y-%m-%d %H:%M:%S")

        if shift['type'] == 1:
            lunch_start = datetime.strptime(shift['lunch_start'], "%Y-%m-%d %H:%M:%S")
            lunch_end = datetime.strptime(shift['lunch_end'], "%Y-%m-%d %H:%M:%S")

            min_lunch_start = start_time + timedelta(hours=route_duration_hours)
            while not (today + timedelta(hours=13) <= min_lunch_start <= today + timedelta(hours=15)):
                min_lunch_start += timedelta(hours=route_duration_hours)
            if lunch_start != min_lunch_start:
                penalty += (min_lunch_start - lunch_start).total_seconds()

            intervals.append((start_time, lunch_start))
            intervals.append((lunch_end, end_time))
        elif shift['type'] == 2:
            for brk in shift['breaks']:
                break_start = datetime.strptime(brk['break_start'], "%Y-%m-%d %H:%M:%S")
                break_end = datetime.strptime(brk['break_end'], "%Y-%m-%d %H:%M:%S")
                intervals.append((start_time, break_start))
                start_time = break_end
            intervals.append((start_time, end_time))
        else:
            intervals.append((start_time, end_time))

    intervals.sort(key=lambda x: x[0])

    for i in range(1, len(intervals)):
        idle_time = (intervals[i][0] - intervals[i - 1][1]).total_seconds()
        if idle_time > 0:
            total_idle_time += idle_time

    if not filter_schedules_with_overlaps(schedule, number_of_buses):
        penalty += 1000

    return total_idle_time + penalty


def select(population, fitness_scores, num):
    """
    Производит селекцию среди популяции.

    :param population: Список расписаний, представляющих текущую популяцию.
    :param fitness_scores: Список приспособленностей.
    :param num: Количество расписаний, которые нужно отобрать.
    :return: Список отобранных расписаний.
    """
    selected = sorted(zip(population, fitness_scores), key=lambda x: x[1])[:num]
    return [x[0] for x in selected]


def crossover(parent1, parent2):
    """
    Производит селекцию среди популяции.

    :param parent1: Первый родитель - расписание, состоящие из расписаний водителей.
    :param parent2: Второй родитель - расписание, состоящие из расписаний водителей.
    :return: Новое расписание.
    """
    if len(parent1) > 1:
        split = random.randint(1, len(parent1) - 1)
        child = parent1[:split] + parent2[split:]
    else:
        split = random.randint(1, len(parent1))
        child = parent1[:split] + parent2[split:]
    return child


def mutate_schedule(schedule):
    """
    Мутирует расписание, сдвигая время начала и окончания смены на 1–2 часа вверх или вниз.

    :param schedule: Расписание водителей (список словарей с параметрами смен).
    :return: Мутированное расписание.
    """
    mutated_schedule = schedule.copy()

    for shift in mutated_schedule:
        shift_amount = random.choice([-2, -1, 1, 2])
        shift_start = datetime.strptime(shift["start_time"], "%Y-%m-%d %H:%M:%S")
        shift_end = datetime.strptime(shift["end_time"], "%Y-%m-%d %H:%M:%S")

        if shift["type"] == 1:
            new_start_time = shift_start + timedelta(hours=shift_amount)

            if new_start_time.hour < 6:
                new_start_time = shift_start.replace(hour=6, minute=0, second=0)
            elif new_start_time.hour > 10:
                new_start_time = shift_start.replace(hour=10, minute=0, second=0)

            new_end_time = shift_end + timedelta(hours=(new_start_time - shift_start).total_seconds() // 3600)
            shift["start_time"] = new_start_time.strftime("%Y-%m-%d %H:%M:%S")
            shift["end_time"] = new_end_time.strftime("%Y-%m-%d %H:%M:%S")

        else:
            new_start_time = shift_start + timedelta(hours=shift_amount)
            new_end_time = shift_end + timedelta(hours=shift_amount)
            shift["start_time"] = new_start_time.strftime("%Y-%m-%d %H:%M:%S")
            shift["end_time"] = new_end_time.strftime("%Y-%m-%d %H:%M:%S")

            for brk in shift['breaks']:
                new_start = datetime.strptime(brk["break_start"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=shift_amount)
                new_end = datetime.strptime(brk["break_end"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=shift_amount)
                brk['break_start'] = new_start.strftime("%Y-%m-%d %H:%M:%S")
                brk['break_end'] = new_end.strftime("%Y-%m-%d %H:%M:%S")

    return mutated_schedule


def filter_schedules_with_overlaps(genetic_schedule, max_overlaps):
    """
    Проверяет расписание на допустимость по числу пересечений.

    :param genetic_schedule: Список расписаний водителей.
    :param max_overlaps: Максимально допустимое число пересечений между расписаниями.
    :return: True, если расписание допустимо, False — если отбраковывается.
    """
    def intervals_overlap(interval1, interval2):
        return interval1[0] < interval2[1] and interval2[0] < interval1[1]

    driver_intervals = {}
    for shift in genetic_schedule:
        driver = shift['driver']
        start_time = datetime.strptime(shift['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(shift['end_time'], "%Y-%m-%d %H:%M:%S")
        intervals = []

        if shift['type'] == 1:
            lunch_start = datetime.strptime(shift['lunch_start'], "%Y-%m-%d %H:%M:%S")
            lunch_end = datetime.strptime(shift['lunch_end'], "%Y-%m-%d %H:%M:%S")
            intervals.append((start_time, lunch_start))
            intervals.append((lunch_end, end_time))
        elif shift['type'] == 2:
            breaks = shift.get('breaks', [])
            last_start_time = start_time
            for brk in breaks:
                break_start = datetime.strptime(brk['break_start'], "%Y-%m-%d %H:%M:%S")
                break_end = datetime.strptime(brk['break_end'], "%Y-%m-%d %H:%M:%S")
                intervals.append((last_start_time, break_start))
                last_start_time = break_end
            intervals.append((last_start_time, end_time))
        else:
            intervals.append((start_time, end_time))

        if driver not in driver_intervals:
            driver_intervals[driver] = []
        driver_intervals[driver].extend(intervals)

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


def genetic_algorithm(drivers, number_of_buses, route_duration, population_size=50, generations=100):
    """
    Реализует генетический алгоритм.

    :param drivers: Количество водителей.
    :param number_of_buses: Количество автобусов.
    :param route_duration: Длительность маршрута.
    :param population_size: Размер популяции.
    :param generations: Количество эпох работы алгоритма
    :return: Расписание водителей.
    """
    population = initialize_population(population_size, drivers, route_duration)

    for generation in range(generations):
        fitness_scores = [calculate_fitness(schedule, number_of_buses, route_duration) for schedule in population]
        next_population = []

        parents = select(population, fitness_scores, population_size // 2)

        for _ in range(population_size // 2):
            parent1, parent2 = random.sample(parents, 2)
            child = crossover(parent1, parent2)
            next_population.append(child)

        for child in next_population:
            if random.random() < 0.1:
                mutate_schedule(child)

        population = parents + next_population

        # Лог текущего поколения
        #print(f"Generation {generation}: Best fitness = {max(fitness_scores)}")

    best_fitness = max([calculate_fitness(schedule, number_of_buses, route_duration) for schedule in population])
    best_schedule = population[[calculate_fitness(schedule, number_of_buses, route_duration) for schedule in population].index(best_fitness)]
    return best_schedule


def duplicate_genetic_schedules(driver_schedules, n_days):
    """
    Дублирует расписания водителей на n дней с учётом выходных.

    :param driver_schedules: Список кортежей (водитель, расписание).
    :param n_days: Количество дней для дублирования расписания.
    :return: Новый список расписаний на n дней.
    """
    extended_schedules = []

    for day in range(n_days):
        for driver_schedule in driver_schedules:
            type_driver = driver_schedule['type']
            driver = driver_schedule['driver']
            if driver.can_work_today():
                new_schedule = copy.deepcopy(driver_schedule)
                start_time = datetime.strptime(str(driver_schedule['start_time']), "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(str(driver_schedule['end_time']), "%Y-%m-%d %H:%M:%S")

                new_start_time = start_time + timedelta(days=day + 1)
                new_end_time = end_time + timedelta(days=day + 1)

                new_schedule['start_time'] = new_start_time
                new_schedule['end_time'] = new_end_time
                if type_driver == 1:
                    new_lunch_start = datetime.strptime(str(driver_schedule['lunch_start']),
                                                        "%Y-%m-%d %H:%M:%S") + timedelta(days=day + 1)
                    new_lunch_end = datetime.strptime(str(driver_schedule['lunch_end']),
                                                      "%Y-%m-%d %H:%M:%S") + timedelta(days=day + 1)
                    new_schedule['lunch_start'] = new_lunch_start
                    new_schedule['lunch_end'] = new_lunch_end
                else:
                    type_2_breaks = []
                    for lunch_break in driver_schedule['breaks']:
                        new_break_start = datetime.strptime(str(lunch_break['break_start']),
                                                            "%Y-%m-%d %H:%M:%S") + timedelta(days=day + 1)
                        new_break_end = datetime.strptime(str(lunch_break['break_end']),
                                                          '%Y-%m-%d %H:%M:%S') + timedelta(days=day + 1)
                        type_2_breaks.append({'break_start': new_break_start, 'break_end': new_break_end})
                    new_schedule['breaks'] = type_2_breaks

                extended_schedules.append(new_schedule)

                driver.update_counters()

    return extended_schedules
