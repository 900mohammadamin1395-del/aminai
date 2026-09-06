# -*- coding: utf-8 -*-

import os

import requests


CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def is_configured():
    return bool(CLIENT_ID and CLIENT_SECRET)


def build_auth_url(redirect_uri, state):

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account"
    }

    query = "&".join(
        key + "=" + requests.utils.quote(str(value), safe="")
        for key, value in params.items()
    )

    return AUTH_URL + "?" + query


def exchange_code(code, redirect_uri):

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    response = requests.post(TOKEN_URL, data=data, timeout=15)
    response.raise_for_status()

    return response.json()


def get_user_email(access_token):

    headers = {
        "Authorization": "Bearer " + access_token
    }

    response = requests.get(USERINFO_URL, headers=headers, timeout=15)
    response.raise_for_status()

    data = response.json()

    return data.get("email"), bool(data.get("email_verified"))
