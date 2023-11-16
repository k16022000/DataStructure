# from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from instamart import models
from .models import Instamart,InstamartPackages,package_contain
from bson import ObjectId
from dataStructure.global_service import DatabaseModel
# Create your views here.


def signUp(request):
    json_response = JSONParser().parse(request)
    item = json_response['SignUpData']
    item_obj = Instamart(**item)
    item_obj.save()
    return JsonResponse(True,safe = False)

def signIn(request):
    json_req = JSONParser().parse(request)
    print(json_req,'json_req=======')
    data_list = list()
    data = dict()
    obj = DatabaseModel.list_documents(Instamart.objects,json_req)
    
    if(obj):
        data['login_status'] = "Login sucsessfull"
        data['email'] = json_req['email']
    else:
        data['login_status'] = "invaild Input"
    data_list.append(data)
    return JsonResponse(data_list,safe = False)

def packageDetails(request):
    packageDetails = dict()
    problem_folder = 'packageDetails'
    uploaded_image = request.FILES.get('upload')
    responseA = DatabaseModel.uploadAndGenerateLinkForImage(request, uploaded_image, problem_folder)
    packageDetails['resource_link'] = responseA['url']
    packageDetails['package'] = request.POST.get('package')
    packageDetails['package_amount'] = request.POST.get('package_amount')
    packageDetails['combo'] = request.POST.get('combo')
    packageDetails['expiry_date'] = request.POST.get('expiry_date')
    # problem_folder_1 = 'packageContains'
    # uploaded_image = request.FILES.get('uploadA')
    # responseB = DatabaseModel.uploadAndGenerateLinkForImage(request, uploaded_image, problem_folder_1)
    packageDetails['package_contains_list'] = list()
    # package_contains_dict = dict()
    # package_contains_dict['resource_link'] = responseB['url']
    # package_contains_dict['name'] = request.POST.get('name')
    # package_contains_dict['packagecontains_amount'] = request.POST.get('packagecontains_amount')
    # package_contains_dict['brand'] = request.POST.get('brand')
    # package_contains_dict['Dimension'] = request.POST.get('Dimension')
    # packageDetails['package_contains_list'].append(package_contains_dict)
    item_obj = InstamartPackages(**packageDetails)
    item_obj.save()
    return JsonResponse(True,safe = False)

def allpackageDetails(request):
    if request.method == 'GET':
        data = dict()
        pipeline = [
            # {
            #     "$match":{
            #         "_id" : {"$in":[ObjectId("650bf167fc9f69059c52a82f")]}
            #     }
            # },
            {
                "$project":{
                    "_id" : 0,
                    "id" : {"$toString" : "$_id"},
                    "expiry_date" : 1,
                    "package_image" : 1,
                    "package" : 1,
                    "package_amount" : 1,
                    "combo" : 1,
                    "resource_link" : 1,
                    # "package_contains_dict" : 1,
                    # "quantity":0
                }
            }
        ]
        pipeline_data = list(InstamartPackages.objects.aggregate(*pipeline))
        data['package_list'] = pipeline_data
        return JsonResponse(data, safe = False)

def savePackageDetails(request):
    problem_folder_1 = 'packageContains'
    uploaded_image = request.FILES.get('upload')
    response = DatabaseModel.uploadAndGenerateLinkForImage(request, uploaded_image, problem_folder_1)
    package_contains_dict = dict()
    package_contains_dict['resource_link'] = response['url']
    package_contains_dict['name'] = request.POST.get('name')
    package_contains_dict['packagecontains_amount'] = request.POST.get('packagecontains_amount')
    package_contains_dict['brand'] = request.POST.get('brand')
    package_contains_dict['Dimension'] = request.POST.get('Dimension')
    package_id = request.POST.get('id')              
    package_contain_obj = DatabaseModel.save_documents(package_contain,package_contains_dict)
    DatabaseModel.update_documents(InstamartPackages.objects,{"id" : ObjectId(package_id)},{"push__package_contains_list" : package_contain_obj.id})
    return JsonResponse(True, safe = False)

def packageItems(request):
    if request.method == 'GET':
        data = dict()
        id = request.GET.get("id")
        # pipeline = [
        #     {
        #         "$match":{
        #             "_id" : {"$in":[ObjectId(id)]}
        #         }
        #     },
        #     {
        #         "$lookup": {
        #             "from": "package_contains",
        #             "localField": "package_contains_list",
        #             "foreignField": "_id",
        #             "as": "package_contains_ins"
        #         }

        #     },

        #     {
        #         "$project":{
        #             "_id" : 0,
        #             "id" : {"toString" : "$_id"},
        #             "expiry_date" : 1,
        #             "package_image" : 1,
        #             "package" : 1,
        #             "package_amount" : 1,
        #             "combo" : 1,
        #             "resource_link" : 1,
        #             "package_contains_list": 1,
        #             "package_contains_ins": {"$map": {"input": "$package_contains_ins", "as": "pc", "in": "$$pc._id"}}
        #         }
        #     }
        # ]
        pipeline = [
           {
                "$match": {
                "_id": {"$in": [ObjectId(id)]}
                }
           },
           {
                "$lookup": {
                "from": "package_contains",
                "localField": "package_contains_list",
                "foreignField": "_id",
                "as": "package_contains_ins"
                }
           },
           {
                "$unwind": {
                "path": "$package_contains_ins",
                "preserveNullAndEmptyArrays": True
                }
           },
           {
                "$group": {
                "_id": "$_id",
                "expiry_date": {"$first": "$expiry_date"},
                "package_image": {"$first": "$package_image"},
                "package": {"$first": "$package"},
                "package_amount": {"$first": "$package_amount"},
                "combo": {"$first": "$combo"},
                "resource_link": {"$first": "$resource_link"},
                "package_contains_list": {"$push": "$package_contains_ins"}
                }
           },
           {
                "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "expiry_date": 1,
                "package_image": 1,
                "package": 1,
                "package_amount": 1,
                "combo": 1,
                "resource_link": 1,
                "package_contains_list": 1
                }
           }
        ]
        pipeline_data = list(InstamartPackages.objects.aggregate(*pipeline))
        # for i in  pipeline_data:
        #     i['package_contains_list'] = [str(j) for j in i.get('package_contains_list', [])]
        data['packageItem_list'] = pipeline_data
        return JsonResponse(data, safe = False)


