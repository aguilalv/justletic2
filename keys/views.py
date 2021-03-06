""" Views to manage Keys for Justletic external services """
import requests
import os
import logging
from structlog import wrap_logger

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from .forms import HeroForm
from .models import Key

from utils.strava_utils import STRAVA_AUTH_ERROR
from utils.strava_utils import exchange_strava_code, get_strava_activities
from utils.spotify_utils import exchange_spotify_code, SPOTIFY_AUTH_ERROR
from accounts.forms import LoginForm, ChangePasswordForm

log = logging.getLogger(__name__)
logger = wrap_logger(log)

def home_page(request):
    """Render Justletic home page"""
    hero_form = HeroForm()
    login_form = LoginForm()
    return render(request, "home.html", {"hero_form": hero_form, "login_form": login_form})

def strava_token_exchange(request):
    """Receives Strava authorisation code and sends request for user token"""
    global logger
    logged_in_user = request.user
    logger = logger.bind(user=logged_in_user.email) 

    code = request.GET.get("code")
    token, strava_id = exchange_strava_code(code)

    if not token or not strava_id:
        messages.add_message(request, messages.ERROR, STRAVA_AUTH_ERROR)
        logger.info("Received Strava error in token exchange")
        return render(request, "home.html")

    new_key = Key(
        user=logged_in_user,
        token=token,
        refresh_token="",
        strava_id=strava_id,
        service=Key.STRAVA
    )
    new_key.save()
    logger.info("Access to Strava authorised")
    return redirect('activity_summary')

def activity_summary(request):
    """Recovers Strava token for logged in user, recover list of activites and present summary of activity"""
    global logger
    logged_in_user = request.user
    logger = logger.bind(user=logged_in_user.email) 
    token = None

    keys = Key.objects.filter(user=logged_in_user) 
    for key in keys:
        if key.service == Key.STRAVA:
            token = key.token

    activities = get_strava_activities(token)
    if activities:
        logger.info("Strava activity summary received") 
        change_password_form = ChangePasswordForm() 
        return render(
            request,
            "congratulations.html",
            {"last_activity_distance": activities[0].get("distance") / 1000,
            "change_password_form": change_password_form,
            },
        )
    else:
        messages.add_message(request, messages.ERROR, STRAVA_AUTH_ERROR)
        logger.info("Received Strava error for activity summary")
        return render(request, "home.html")

def spotify_token_exchange(request):
    """Receives Spotify authorisation code and sends request for user token"""
    global logger
    logged_in_user = request.user
    logger = logger.bind(user=logged_in_user.email) 
    code = request.GET.get("code")
    token, refresh_token = exchange_spotify_code(code)
    if not token or not refresh_token:
        messages.add_message(request, messages.ERROR, SPOTIFY_AUTH_ERROR)
        logger.info("Received Spotify error in token exchange")
        return render(request, "home.html")
    
    new_key = Key(
        user=logged_in_user,
        token=token,
        refresh_token=refresh_token,
        strava_id="",
        service=Key.SPOTIFY
    )
    new_key.save()
    logger.info("Access to Spotify authorised")

    return render(request,"user_summary.html")
