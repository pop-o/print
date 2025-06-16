from django.urls import path
from function.views import PrintImageView

urlpatterns = [
    path("print/", PrintImageView.as_view(), name="print"),
]
