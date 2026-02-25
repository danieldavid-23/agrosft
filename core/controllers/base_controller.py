from django.http import JsonResponse
from django.views import View
import json

class BaseController(View):
    def json_response(self, data, status=200):
        return JsonResponse(data, status=status, safe=False)
    
    def get_request_data(self, request):
        if request.method == 'GET':
            return request.GET.dict()
        elif request.method == 'POST':
            if request.content_type == 'application/json':
                return json.loads(request.body)
            return request.POST.dict()
        return {}
