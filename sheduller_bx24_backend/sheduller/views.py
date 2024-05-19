from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import requests
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


@csrf_exempt
@require_POST
def get_elements(request):
    try:
        data = json.loads(request.body)

        dateFrom = data.get('dateFrom')
        dateTo = data.get('dateTo')
        rooms = data.get('rooms')

        if not dateFrom or not dateTo or not rooms:
            raise ValidationError("Missing required fields: dateFrom, dateTo, or rooms.")

        # Дополнительно можно добавить валидацию форматов дат и массива чисел

        # Отправляем запрос к стороннему API
        api_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.element.get.json"
        params = {
            "IBLOCK_TYPE_ID": "lists",
            "IBLOCK_ID": "78",
            "SECTION_ID": "0"
        }

        response = requests.post(api_url, params=params)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch data from API.'}, status=500)

        api_data = response.json()

        # Обрабатываем ответ
        transformed_data = []
        for item in api_data['result']:
            transformed_item = {
                'id': int(item['ID']),
                'color': list(item['PROPERTY_318'].values())[0],
                'title': item['NAME'],
                'section': int(item['IBLOCK_SECTION_ID']),
                'dateFrom': list(item['PROPERTY_316'].values())[0],
                'dateTo': list(item['PROPERTY_317'].values())[0]
            }
            transformed_data.append(transformed_item)

        return JsonResponse(transformed_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def get_sections(request):
    try:
        # Отправляем запрос к стороннему API
        api_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.section.get.json"
        params = {
            "IBLOCK_TYPE_ID": "lists",
            "IBLOCK_ID": "78"
        }

        response = requests.post(api_url, params=params)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch data from API.'}, status=500)

        api_data = response.json()

        # Обрабатываем ответ
        transformed_data = []
        for item in api_data['result']:
            transformed_item = {
                'id': int(item['ID']),
                'title': item['NAME']
            }
            transformed_data.append(transformed_item)

        return JsonResponse(transformed_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
@require_POST
def report_day(request):
    try:
        data = json.loads(request.body)
        date = data.get('date')

        if not date:
            return JsonResponse({'error': 'Missing required field: date'}, status=400)

        # Форматируем начало и конец дня
        start_date = datetime.strptime(date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        end_date = start_date.replace(hour=23, minute=59, second=59)

        api_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/crm.deal.list"
        headers = {'Content-Type': 'application/json'}
        body = {
            "select": [
                "ID",
                "TITLE",
                "STAGE_ID",
                "UF_CRM_1715508611",  # Комната
                "UF_CRM_1715507748",  # Филиал
                "UF_CRM_DEAL_1712137850471",  # Дата начала
                "UF_CRM_DEAL_1712137877584"  # Дата окончания
            ],
            "filter": {
                'CATEGORY_ID': 7,
                '!=STAGE_ID': 'C7:NEW',
                '>=UF_CRM_DEAL_1712137850471': start_date.isoformat(),
                '<=UF_CRM_DEAL_1712137877584': end_date.isoformat()
            }
        }

        response = requests.post(api_url, headers=headers, json=body)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch data from API.'}, status=500)

        api_data = response.json()

        # Преобразование данных
        transformed_data = []
        for item in api_data['result']:
            transformed_item = {
                'id': item['ID'],
                'title': item['TITLE'],
                'room': item['UF_CRM_1715508611'],
                'build': item['UF_CRM_1715507748'],
                'dateFrom': item['UF_CRM_DEAL_1712137850471'],
                'dateTo': item['UF_CRM_DEAL_1712137877584']
            }
            transformed_data.append(transformed_item)

        return JsonResponse(transformed_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)