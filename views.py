from django.shortcuts import render, redirect
from django.db import connection, connections
from django.http import HttpResponse, JsonResponse
import json
import datetime

def public_hc(request):
    return HttpResponse('Ok')

def importer_asin_ht(request):
    return render(request, 'df_importer.html', {'user': user_checkpoint(request)})

def importer_asin(request):
    items = json.loads(request.body)['items']
    if items:
        status_code, ret = post_asin(json.loads(request.body)['items'], user_checkpoint(request))
        if "ok" in status_code:
            return JsonResponse({'ret': 'Successfully uploaded!'}, status=200)
        else:
            return JsonResponse({'ret': ret}, status=409)
    else:
        print('test')
    return render(request, 'df_importer.html', {'user': 'rk'})

def post_asin(data, user):
    batch_no = (datetime.datetime.now() + datetime.timedelta(hours=4)).strftime("%Y%m%d%H%M%S%f")
    data = [dict(item, **{'created_by': user, 'batch_no': batch_no}) for item in data]
    ex_headers = ",".join(['%({})s'.format(k) for k in data[0].keys()])
    up_headers = ",".join(['%s = VALUES(%s)' % (k, k) for k in data[0].keys() if k == 'is_valid'])
    if up_headers:
        query = "UPDATE scrapify.import_raw SET is_valid=%(is_valid)s, is_active=%(is_active)s WHERE asin=%(asin)s;"
    else:
        query = "INSERT INTO scrapify.import_raw (%s) VALUES (%s);" % (",".join(list(data[0].keys())), ex_headers)
    return insert_bulk(query, data)

def importer_data_ht(request):
    return render(request, 'df_data.html', {'user': user_checkpoint(request)})

def importer_data(request):
    items = json.loads(request.body).get('items', [])
    if items:
        status_code, ret = post_data(items, user_checkpoint(request))
        if "ok" in status_code:
            return JsonResponse({'ret': 'Successfully uploaded!'}, status=200)
        else:
            return JsonResponse({'ret': ret}, status=409)
    else:
        print('test')
    return render(request, 'df_data.html', {'user': 'UZ'})

def post_data(data, user):
    batch_no = (datetime.datetime.now() + datetime.timedelta(hours=4)).strftime("%Y%m%d%H%M%S%f")
    data = [dict(item, created_by=user, batch_no=batch_no) for item in data]
    
    columns = data[0].keys()
    ex_headers = ",".join([f'%({k})s' for k in columns])
    up_headers = ",".join([f'{k} = VALUES({k})' for k in columns])
    
    query = f"""
        INSERT INTO scrapify.import_data ({','.join(columns)}) 
        VALUES ({ex_headers}) 
        ON DUPLICATE KEY UPDATE {up_headers}
    """
    
    status, message = insert_bulk(query, data)
    
    if status == "ok":
        transfer_status, transfer_message = transfer_data()
        if transfer_status == "ok":
            return "ok", "Successfully uploaded and transferred!"
        else:
            return "failed", transfer_message
    else:
        return status, message

def user_checkpoint(request):
    return request.META.get('HTTP_X_FORWARDED_USER', 'scrapify-test@noon.com')

def insert_bulk(query, data):
    try:
        cursor = connection.cursor()
        if data:
            cursor.executemany(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        return "ok", "Submitted Successfully!"
    except Exception as inst:
        print(str(inst))
        return "failed", str(inst)

def transfer_data():
    query = """
    INSERT INTO import_raw (
        asin, id_partner, partner_sku, country, price, stock, batch_no, 
        is_valid, is_active, created_by, created_at, updated_at
    )
    SELECT 
        asin, id_partner, partner_sku, country, price, stock, batch_no, 
        is_valid, is_active, created_by, created_at, updated_at
    FROM import_data
    ON DUPLICATE KEY UPDATE
        asin = VALUES(asin),
        id_partner = VALUES(id_partner),
        partner_sku = VALUES(partner_sku),
        country = VALUES(country),
        price = VALUES(price),
        stock = VALUES(stock),
        batch_no = VALUES(batch_no),
        is_valid = VALUES(is_valid),
        is_active = VALUES(is_active),
        created_by = VALUES(created_by),
        created_at = VALUES(created_at),
        updated_at = VALUES(updated_at);
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        return "ok", "Successfully transferred data from import_data to import_raw"
    except Exception as e:
        return "failed", str(e)
