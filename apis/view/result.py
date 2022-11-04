from common.base.base_respons import retJson
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def calculate(request):
    return retJson()
