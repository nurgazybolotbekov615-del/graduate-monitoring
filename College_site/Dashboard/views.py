from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count
from .models import Student
import json

import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

from reportlab.pdfgen import canvas

matplotlib.use('Agg')

def map_view(request):

    students = Student.objects.all()

    data = []

    for s in students:

        lat, lng = get_coordinates(s.city)

        if lat is None or lng is None:
            continue

        data.append({
            "name": s.name,
            "city": s.city,
            "status": s.status,
            "lat": lat,
            "lng": lng
        })

    return render(request, "map.html", {
        "students": data
    })


def download_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    p = canvas.Canvas(response)

    students = Student.objects.all()

    y = 800

    p.setFont("Helvetica", 14)
    p.drawString(200, y, "Отчёт трудоустройства выпускников")

    y -= 50

    for student in students:

        text = f"{student.name} | {student.group} | {student.status}"

        p.drawString(100, y, text)

        y -= 25

    p.showPage()
    p.save()

    return response

def sync_google_forms(request):

    url = "https://docs.google.com/spreadsheets/d/1ztiu-lyexA1wX1J1Vy1UXSCQbrR6K6tIP3PpUTArXnY/export?format=xlsx"

    df = pd.read_excel(url)

    # убрать лишние пробелы
    df.columns = df.columns.str.strip()

    print(df.columns)   # покажет названия колонок в терминале

    status_map = {
        "Да": "work",
        "Учусь": "study",
        "Армия": "army",
        "Нет": "unemployed"
    }

    for _, row in df.iterrows():

        status = status_map.get(
            str(row.get('Вы трудоустроены?', '')).strip(),
            "unemployed"
        )

        city = row.get('Где вы работаете?', 'Unknown')

        Student.objects.update_or_create(

            name=row.get('Ф.И.О', ''),
            group=row.get('Группа', ''),
            graduation_year=row.get('Выпустил', 0),

            defaults={
                "status": status,
                "city": city
            }
        )

    return redirect('analytics')

def analytics(request):

    students = Student.objects.all()

    # статус студентов
    data = students.values('status').annotate(count=Count('status'))
    labels = [item['status'] for item in data]
    values = [item['count'] for item in data]

    # статистика по годам
    year_data = students.values('graduation_year').annotate(count=Count('id')).order_by('graduation_year')
    year_labels = [str(item['graduation_year']) for item in year_data]
    year_values = [item['count'] for item in year_data]

    # статистика по группам
    group_data = students.values('group').annotate(count=Count('id')).order_by('group')
    group_labels = [item['group'] for item in group_data]
    group_values = [item['count'] for item in group_data]

    total = students.count()
    work = students.filter(status='work').count()
    study = students.filter(status='study').count()
    army = students.filter(status='army').count()
    unemployed = students.filter(status='unemployed').count()

    return render(request, 'analytics.html', {
        'labels': json.dumps(labels),
        'values': json.dumps(values),
        'year_labels': json.dumps(year_labels),
        'year_values': json.dumps(year_values),
        'group_labels': json.dumps(group_labels),
        'group_values': json.dumps(group_values),
        'total': total,
        'work': work,
        'study': study,
        'army': army,
        'unemployed': unemployed
    })

def home(request):

    total = Student.objects.count()

    return render(request, 'home.html', {
        'total': total
    })


def upload_excel(request):

    if request.method == 'POST' and request.FILES.get('file'):

        file = request.FILES['file']
        df = pd.read_excel(file)

        df.columns = df.columns.str.strip()

        status_map = {
            "Да": "work",
            "Работаю": "work",
            "Учусь": "study",
            "Армия": "army",
            "Нет": "unemployed",
            "Безработный": "unemployed"
        }

        for _, row in df.iterrows():

            status = status_map.get(
                str(row['Вы трудоустроен?']).strip(),
                "unemployed"
            )

            Student.objects.create(
                name=row['Ф.И.О'],
                group=row['Группа'],
                graduation_year=row['Выпустил'],
                status=status
            )
            

        return redirect('home')

    return render(request, 'upload.html')

def export_excel(request):

    students = Student.objects.all().values(
        'name',
        'group',
        'status',
        'graduation_year'
    )

    df = pd.DataFrame(students)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=students_report.xlsx'

    df.to_excel(response, index=False)

    return response

def students_list(request):

    students = Student.objects.all()

    search = request.GET.get('search')
    group = request.GET.get('group')

    if search:
        students = students.filter(name__icontains=search)

    if group:
        students = students.filter(group=group)

    groups = Student.objects.values_list('group', flat=True).distinct()

    return render(request, 'students.html', {
        'students': students,
        'groups': groups
    })

def ai_analysis(request):

    students = Student.objects.all()

    total = students.count()
    work = students.filter(status='work').count()
    study = students.filter(status='study').count()
    unemployed = students.filter(status='unemployed').count()

    if total > 0:
        employment_rate = round((work / total) * 100, 1)
    else:
        employment_rate = 0

    if employment_rate > 70:
        ai_text = f"Высокий уровень трудоустройства ({employment_rate}%)."
    elif employment_rate > 40:
        ai_text = f"Средний уровень трудоустройства ({employment_rate}%). Рекомендуется усилить карьерную поддержку."
    else:
        ai_text = f"Низкий уровень трудоустройства ({employment_rate}%). Требуется работа с работодателями."

    return render(request, "ai_analysis.html", {
        "total": total,
        "work": work,
        "study": study,
        "unemployed": unemployed,
        "ai_text": ai_text
    })

def groups(request):

    groups = Student.objects.values_list(
        'group', flat=True
    ).distinct()

    return render(request, 'groups.html', {
        'groups': groups
    })

def get_coordinates(city):

    if not city:
        return None, None

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "college-map-project"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code != 200:
            return None, None

        data = response.json()

        if len(data) == 0:
            return None, None

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])

        return lat, lon

    except Exception as e:
        print("Ошибка геолокации:", e)
        return None, None
    
def ai_chat(request):

    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    history = request.session["chat_history"]

    if request.method == "POST":

        question = request.POST.get("question")

        students = Student.objects.all()

        total = students.count()
        work = students.filter(status="work").count()
        study = students.filter(status="study").count()
        unemployed = students.filter(status="unemployed").count()

        answer = ""

        if "группа" in question.lower():

            groups = students.values('group').distinct().count()
            answer = f"Всего групп выпускников: {groups}"

        elif "2024" in question:

            year_students = students.filter(graduation_year=2024)

            groups = year_students.values('group').distinct().count()
            count = year_students.count()

            answer = f"В 2024 году колледж окончили {count} студентов из {groups} групп."

        elif "работают" in question.lower():

            answer = f"Всего трудоустроены {work} выпускников."

        else:

            answer = f"Всего выпускников: {total}. Работают: {work}, Учится: {study}, Безработные: {unemployed}"

        history.append({
            "question": question,
            "answer": answer
        })

        request.session["chat_history"] = history

    return render(request,"ai_chat.html",{
        "history": history
    })

def clear_chat(request):

    request.session["chat_history"] = []

    return redirect("ai_chat")