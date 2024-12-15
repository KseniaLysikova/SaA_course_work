from openpyxl import Workbook


def save_brute_schedule_to_excel(full_schedule, file_name):
    wb = Workbook()
    ws = wb.active
    ws.title = "Расписание"

    ws.append(["Имя водителя", "Время", "Событие"])

    for entry in full_schedule:
        if isinstance(entry, tuple) and len(entry) == 3:
            driver_obj, driver_name, schedule = entry
            for time, event in schedule:
                ws.append([driver_name, time.strftime('%Y-%m-%d %H:%M:%S'), event])
            ws.append([])

    wb.save(file_name)


def save_genetic_schedule_to_excel(schedule_list, file_name):
    wb = Workbook()
    ws = wb.active
    ws.title = "Расписание"

    ws.append(["ID водителя", "Тип", "Описание", "Значение"])

    for schedule in schedule_list:
        driver_id = schedule['driver_id']
        driver_type = schedule['type']

        if driver_type == 1:
            ws.append([driver_id, driver_type, "Начало смены", schedule['start_time']])
            ws.append([driver_id, driver_type, "Начало обеда", schedule['lunch_start']])
            ws.append([driver_id, driver_type, "Конец обеда", schedule['lunch_end']])
            ws.append([driver_id, driver_type, "Конец смены", schedule['end_time']])
            ws.append([])
        else:
            ws.append([driver_id, driver_type, "Начало смены", schedule['start_time']])
            ws.append([driver_id, driver_type, "Конец смены", schedule['end_time']])

            for lunch_break in schedule['breaks']:
                ws.append([driver_id, driver_type, "Начало перерыва", lunch_break['break_start']])
                ws.append([driver_id, driver_type, "Конец перерыва", lunch_break['break_end']])
            ws.append([])

    wb.save(file_name)
