# from django.shortcuts import render

# Create your views here.
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from app1 import models
from .models import items
from app1.default_serializer import getDefaultSerializer
from bson import ObjectId
from dataStructure.global_service import DatabaseModel
def saveItems(request):
    json_response = JSONParser().parse(request)
    item = json_response['item']
    item_obj = items(**item)
    item_obj.save()
    return JsonResponse(True,safe = False)

def allitemsList(request):
    # u_id = request.GET.get("u_id")
    if request.method == 'GET':
        data = dict()
        pipeline = [
            # {
            #     "$match":{
            #         "_id" : {"$in":[ObjectId("650bf167fc9f69059c52a82f"),ObjectId("652138c3e97c92d0e5cbc88c")]}
            #     }
            # },
            {
                "$project":{
                    "_id" : 0,
                    "id" : {"$toString" : "$_id"},
                    "name" : 1,
                    # "quantity":0
                }
            }
        ]
        pipeline_data = list(items.objects.aggregate(*pipeline))
        print(pipeline_data)
        data['item_list'] = pipeline_data
        return JsonResponse(data, safe = False)

def saveParticularItem(request):
    json_response = JSONParser().parse(request)
    print(json_response)
    # edit_obj = items.objects(id = ObjectId(json_response['id'])).update(name = json_response['name'])
    DatabaseModel.update_documents(items.objects,{"id" : ObjectId(json_response['id'])},{"name" : json_response['name']})
    return JsonResponse(True, safe = False)

def removeItem(request):
    json_response = JSONParser().parse(request)
    # remove_obj = items.objects(id = ObjectId(json_response['id']))
    # remove_obj.delete()
    DatabaseModel.delete_documents(items.objects,{"id" : ObjectId(json_response['id'])})
    return JsonResponse(True, safe = False)

# def sortnamelist(request):
#     json_response = JSONParser().parse(request)
#     sort_by = json_response['sort_by']
#     sorted_documents = DatabaseModel.list_documents(items.objects,{},[],[sort_by])  
#     return JsonResponse(True, safe=False)

def sortnamelist(request):
      json_response = JSONParser().parse(request)
      sort_order = json_response.get('sort_order', 'asc')
      sort_by = json_response.get('sort_by', 'name')
      items_queryset = items.objects.all().order_by(sort_order + sort_by)
      sorted_items = [{'name': item.name, 'id': item.id} for item in items_queryset]
      return JsonResponse({'item_list': sorted_items}, safe=False)
    

