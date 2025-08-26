from django.urls import path
from interactions.views.public import *

urlpatterns = [
    path('sse/stream/', sse_stream, name='sse_stream'),
    path('sse/ping/', sse_ping, name='sse_ping'),
]
