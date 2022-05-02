from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator

from my_proj.amberflo.decorator import count_api_calls


@count_api_calls
def get_foo(request):
    if request.method == "GET":
        return JsonResponse({"foo": "bar"})
    raise JsonResponse({"error": "method not allowed"})


class Bar(View):
    @method_decorator(count_api_calls)
    def get(self, request):
        return JsonResponse({"bar": "foo"})
