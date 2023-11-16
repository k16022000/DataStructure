from django.urls import path
from instamart import views
from .views import signUp,signIn,packageDetails,allpackageDetails,savePackageDetails,packageItems

urlpatterns = [
    path('signUp/',signUp),
    path('signin/',signIn),
    path('packageDetails/',packageDetails),
    path('allpackageDetails/',allpackageDetails),
    path('savePackageDetails/',savePackageDetails),
    path('packageItems/',packageItems),
]