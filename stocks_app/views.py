from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def homepage_route(request):
    '''
        @description Main page of the website

    '''
    return render(request, 'homepage.html.j2', context={
        'title' : "homepage",
    })


def about_route(request):
    '''
        @description about page of the website

    '''
    return render(request, 'about.html.j2', context={
        'title' : "about us",
    })


def contact_route(request):
    '''
        @description contact page of the website

    '''
    return render(request, 'contact.html.j2', context={
        'title' : "contact",
    })


def method_route(request):
    '''
        @description Main page of the website

    '''
    return render(request, 'methodology.html.j2', context={
        'title' : "methodology",
    })
