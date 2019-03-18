import csv
import os
import datetime

from django.shortcuts import render
from django import forms
from dijkstra_path1 import go


class AddressEntry(forms.Form):
    '''
    '''
    start_address = forms.CharField(
        label= "Start Address",
        help_text= "e.g. 1234 N Main St.",
        required= True)
    end_address = forms.CharField(
        label= "End Address",
        help_text= "e.g. 5000 N Main St.",
        required= True)
    date_of_travel = forms.CharField(
        label= "Date of Travel",
        help_text= "e.g. 2010-02-28",
        required=False)
    hour_of_travel = forms.IntegerField(
        label= "Hour of Travel",
        help_text= "e.g. 14",
        required=False)
    temperature = forms.IntegerField(
        label= "Temperature at Time of Travel (F)",
        help_text= "e.g. 37",
        required=False)
    precipitation = forms.IntegerField(
        label= "Precipitation at Time of Travel (Inches)",
        help_text = "e.g. 4",
        required=False)


def plot_route(request):
    '''
    Takes in the submission request, calls our routing function, and ouputs:
    {route_info}: a dictionary containing:
        - start_address: (string) starting location
        - end_address: (string) ending location
        - date_of_travel: (string) date of travel, None if none entered
        - hour_of_travel: (int) hour of travel, None if none entered
        - temperature: (int) temperature (F) of travel, None if none entered
        - precipitation: (int) precipitation (inches), None if none entered
    '''
    route_info = {}
    route = []
    if request.method == 'GET':
        form = AddressEntry(request.GET)
        route_info['response'] = form
        if form.is_valid():
            args = {}
            args["start_address"] = form.cleaned_data['start_address']
            args["end_address"] = form.cleaned_data['end_address']
            args["date_of_travel"] = form.cleaned_data.get('date_of_travel',\
                                                            None)
            args["hour_of_travel"] = form.cleaned_data.get('hour_of_travel',\
                                                            None)
            args["temperature"] = form.cleaned_data.get('temperature',\
                                                         None)
            args["precipitation"] = form.cleaned_data.get('precipitation',\
                                                           None)
            route, relative_score = go(args)
            if type(route) == str:
                route_info['error'] = route
                route_info['relative_score'] = "No score can be computed."
            else:
                route_info['route'] = route
                route_info['start_address'] = form.cleaned_data['start_address']
                route_info['end_address'] = form.cleaned_data['end_address']
                route_info['relative_score'] = "Your path is safer than " +\
                                                str(round(relative_score)) +\
                                                "% of all paths in Chicago."
    route_info['address_form'] = form

    return render(request, 'routemanager/index.html', route_info)