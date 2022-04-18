import datetime
# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core import models
from core.sites.echo import parsing_radio_echo, RADIO_URL as ECHO_RADIO_URL
from core.sites.radio import parsing_radio, RADIO_URL
from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
from core.sites.svoboda import parsing_radiosvoboda, RADIO_URL as SVOBODA_RADIO_URL
from core.sites.utils import update_proxy, stop_proxy, get_md5_text, get_sphinx_id, save_articles, get_late_date


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_echo(request):
    articles, proxy = parsing_radio_echo(get_late_date(ECHO_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ECHO_RADIO_URL, articles)
    return Response("Ok")

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test(request):

    return Response("Ok")

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def text(request):
    from core.utils.parsing_smi_url import parsing_smi_url
    url = request.data['urls']
    try:
        res = parsing_smi_url(url, attempts=0)
        if res:
            return HttpResponse(res)
        return HttpResponse("")
    except Exception as e:
        return HttpResponse("")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radio(request):
    articles, proxy = parsing_radio(get_late_date(RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radiozenit(request):
    articles, proxy = parsing_radio_zenit(get_late_date(ZENIT_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ZENIT_RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radiosvodoba(request):
    articles, proxy = parsing_radiosvoboda(get_late_date(SVOBODA_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(SVOBODA_RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_echo_full(request):
    articles, proxy = parsing_radio_echo(get_late_date(None), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ECHO_RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radio_full(request):
    articles, proxy = parsing_radio(get_late_date(None), update_proxy(None))
    stop_proxy(proxy)
    save_articles(RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radiozenit_full(request):
    articles, proxy = parsing_radio_zenit(get_late_date(None), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ZENIT_RADIO_URL, articles)
    return Response("Ok")


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_radiosvodoba_full(request):
    articles, proxy = parsing_radiosvoboda(get_late_date(None), update_proxy(None))
    stop_proxy(proxy)
    save_articles(SVOBODA_RADIO_URL, articles)
    return Response("Ok")
