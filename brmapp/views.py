# from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from brmapp import models
from .models import Books
from bson import ObjectId
from dataStructure.global_service import DatabaseModel
# Create your views here.
def storeBookDetails(request):
    json_response = JSONParser().parse(request)
    item = json_response['booksItems']
    item_obj = Books(**item)
    item_obj.save()
    return JsonResponse(True,safe = False)

def allbookList(request):
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
                    "title" : 1,
                    "price" : 1,
                    # "quantity":0
                }
            }
        ]
        pipeline_data = list(Books.objects.aggregate(*pipeline))
        data['book_list'] = pipeline_data
        return JsonResponse(data, safe = False)

def saveParticularBook(request):
    json_response = JSONParser().parse(request)
    DatabaseModel.update_documents(Books.objects,{"id" : ObjectId(json_response['id'])},{"title" : json_response['title'],"price" : json_response['price']})
    return JsonResponse(True, safe = False)

def removeBook(request):
    json_response = JSONParser().parse(request)
    print(json_response)
    DatabaseModel.delete_documents(Books.objects,{"id" : ObjectId(json_response['id'])})
    return JsonResponse(True, safe = False)
