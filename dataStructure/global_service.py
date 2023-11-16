from django.http import JsonResponse
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

class DatabaseModel():
    def list_documents(queryset,filter={},field_list=[],sort_list = [],lower_limit = None, upper_limit = None):
        data = queryset(**filter).skip(lower_limit).limit(upper_limit - lower_limit if lower_limit != None and upper_limit != None else None).only(*field_list).order_by(*sort_list)
        return data
    
    def list_distinct_documents(queryset,filter=""):
        data = queryset.distinct(filter)
        return data


    def get_document(queryset,filter={},field_list=[]):
        data = queryset(**filter).only(*field_list)
        if len(data):
            return data[0]
        return None

    def update_documents(queryset, filter={}, json={}):
        data = queryset(**filter).update(**json)
        return bool(data)
    
    def update_domain(domain_name):
        field_names = [name for name in domain_name._fields.keys()]
        for field_name in field_names:
            DatabaseModel.update_documents(domain_name.objects, {field_name + "__exists": False}, {field_name: getattr(domain_name, field_name).default})

    def save_documents(queryset,  json={}):
        obj = queryset(**json)
        try:
            obj.save()
            return obj
        except ValidationError as e:
            raise e

    def delete_documents(queryset,  json={}):
        queryset(**json).delete()
        return True

    def count_documents(queryset,filter={}):
        count = queryset(**filter).count()
        return count
        
    def save_list_documents(queryset, list_object):
        data = queryset.objects.insert(list_object)
        return data

    def cascade_save_documents(queryset,  json={}):
        obj = queryset(**json)
        try:
            # obj.cascade_save()
            obj.save(cascade = True)
            return obj
        except ValidationError as e:
            raise e
    def get_query_document(queryset, filter, field_list=[]):
        data = queryset(filter).only(*field_list)
        if len(data):
            return data[0]
        return None
    
    def create_pipeline(join_fields):
        pipeline = []

        for join_field in join_fields:
            match_criteria = join_field.get('match_criteria')
            lookup_stage = join_field.get('lookup_stage')
            group_stage = join_field.get('group_stage')
            unset = join_field.get('unset')
            add_fields = join_field.get('add_fields')
            project_stage = join_field.get('project_stage')
            sort = join_field.get('sort')
            limit = join_field.get('limit')
            skip = join_field.get('skip')
            

            if match_criteria:
                match_stage = {
                    '$match': match_criteria
                }
                pipeline.append(match_stage)


            if lookup_stage:
                lookup_stage = {
                    '$lookup': {
                        'from': lookup_stage['from_domain'],
                        'localField': lookup_stage['local_field'],
                        'foreignField': lookup_stage['foreign_field'],
                        'as': lookup_stage['as_field']
                    }
                }
                pipeline.append(lookup_stage)
                pipeline.append({'$unwind': f"${lookup_stage['$lookup']['as']}"})

            if group_stage:
                group_stage = {
                    '$group': group_stage
                }
                pipeline.append(group_stage)
            
            if unset:
                unset = {
                    '$unset' : unset    
                }
                pipeline.append(unset)
            if sort: 
                sort = {'$sort': sort}
                pipeline.append(sort)
            if skip:
                skip = {"$skip" : skip}
                pipeline.append(skip)
            if limit: 
                limit = {'$limit': limit}
                pipeline.append(limit)
            if add_fields:
                add_fields = {"$addFields" : add_fields}
                pipeline.append(add_fields)
            if project_stage:
                project_stage = {
                    "$project" : project_stage
                }
                pipeline.append(project_stage)

        return pipeline

    def join_list_documents(queryset, join_fields):
        pipeline = DatabaseModel.create_pipeline(join_fields)
        results = list(queryset.objects.aggregate(*pipeline))
        return results
    
    def join_document(queryset, join_fields):
        pipeline = DatabaseModel.create_pipeline(join_fields)
        results = list(queryset.objects.aggregate(*pipeline))
        if len(results) > 0:
            return results[0]
        return None
    
    def count_join_documents(queryset, join_fields):
        pipeline = DatabaseModel.create_pipeline(join_fields)
        pipeline.append({"$count" : "count"})
        results = list(queryset.objects.aggregate(*pipeline))
        if len(results) > 0: 
            return results[0]["count"]
        return 0

    def update_and_get_document(querySet, filter, static_fields,increment_field,lists,project = None,):
        updated_dict = dict()
        value = []
        if project: 
            value = dict.fromkeys(project, True)
        if static_fields:
            updated_dict["$set"] = static_fields
        if increment_field:
            updated_dict["$inc"] = increment_field
        if lists:
            updated_dict["$push"] = lists
        data = querySet._get_collection().find_one_and_update(filter,updated_dict,projection = value,return_document= True,upsert= True)
        return data

    def uploadAndGenerateLinkForImage(request, uploaded_image, problem_folder):
        # uploaded_image = request.FILES.get('upload')
        scheme = request.scheme
        server_ip = request.META.get('HTTP_HOST', '127.0.0.1')
        link_url = f"{scheme}://{server_ip}"
        if uploaded_image != None:
        # problem_folder = 'problem'
            quiz_folder_path = os.path.join(settings.MEDIA_ROOT, 'images')
            if not os.path.exists(quiz_folder_path):
                os.mkdir(quiz_folder_path)

            problem_path = os.path.join(quiz_folder_path, problem_folder)
            if not os.path.exists(problem_path):
                os.mkdir(problem_path)

            fs = FileSystemStorage(location = problem_path)
            filename = uploaded_image.name
            if fs.exists(filename):
                base_name, extension = os.path.splitext(filename)
                index = 1
                while fs.exists(f"{base_name}_({index}){extension}"):
                    index += 1
                filename = f"{base_name} ({index}){extension}"
            saved_image_file = fs.save(filename, uploaded_image)

            file_path = fs.path(saved_image_file)
            relative_path = os.path.relpath(file_path)
            image_link = f"{link_url}/{relative_path}"
            response = {"url" : image_link, "uploaded" : True}
        else:
            response = {"url":"No image","uploaded" : False}
        return response
        
        
def saveOrUpdateFileDocument(object_ins, field_name, file_obj, file_name):
    file_ins = getattr(object_ins,field_name)
    # data = dict()   
    if file_ins != None: 
        file_ins.replace(file_obj, filename=file_name)
        # data['is_updated'] = True
    else:
        file_ins.put(file_obj, filename = file_name)
        # data['is_created'] = True
    object_ins.save()
    return True

class HrlModelSerializer():
    # @removeNoneValuesFromSerializedData
    def list_documents_serializer(serializer, queried_data):
        serializer_data = serializer(queried_data, many=True).data
        return serializer_data
    
    # @removeNoneValuesFromSerializedData
    def get_documents_serializer(serializer, queried_data):
        serializer_data = serializer([queried_data], many=True).data
        if len(serializer_data):
            return serializer_data[0]
        return None

# class HrlUploadAndGenerateLinkForImage():
#     def uploadAndGenerateLinkForImage(uploaded_image, problem_folder):
#         uploaded_image = request.FILES.get('uploadA')
#         scheme = request.scheme
#         server_ip = request.META.get('HTTP_HOST', '127.0.0.1')
#         link_url = f"{scheme}://{server_ip}"
#         if uploaded_image != None:
#         # problem_folder = 'problem'
#             quiz_folder_path = os.path.join(settings.MEDIA_ROOT, 'images')
#             if not os.path.exists(quiz_folder_path):
#                 os.mkdir(quiz_folder_path)

#             problem_path = os.path.join(quiz_folder_path, problem_folder)
#             if not os.path.exists(problem_path):
#                 os.mkdir(problem_path)

#             fs = FileSystemStorage(location = problem_path)
#             filename = uploaded_image.name
#             if fs.exists(filename):
#                 base_name, extension = os.path.splitext(filename)
#                 index = 1
#                 while fs.exists(f"{base_name}_({index}){extension}"):
#                     index += 1
#                 filename = f"{base_name} ({index}){extension}"
#             saved_image_file = fs.save(filename, uploaded_image)

#             file_path = fs.path(saved_image_file)
#             relative_path = os.path.relpath(file_path)
#             image_link = f"{link_url}/{relative_path}"
#             response = {"url" : image_link, "uploaded" : True}
#         else:
#             response = {"url":"No image","uploaded" : False}
#         return response