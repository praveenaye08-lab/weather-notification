"""
Weather Email Notifier
-----------------------
Fetches the current temperature from Open-Meteo for a fixed location
(latitude -5, longitude 120) and emails the result via Gmail SMTP.

SETUP:
1. Replace SENDER_EMAIL, SENDER_APP_PASSWORD, and RECEIVER_EMAIL below.
2. SENDER_APP_PASSWORD must be a Gmail "App Password", not your normal
   Gmail password. Generate one at: https://myaccount.google.com/apppasswords
   (requires 2-Step Verification to be enabled on the Gmail account).
3. Install dependency: pip install requests
4. Run: python weather_email.py
"""

import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

# ==========================================================
# CONFIGURATION - replace these values with your own details
# ==========================================================
SENDER_EMAIL = "praveenmoorthy79@gmail.com"          # Your Gmail address
SENDER_APP_PASSWORD = "unrs zxft bvwi gxdn"      # Gmail App Password (16 chars)
RECEIVER_EMAIL = "praveenaye08@gmail.com"  # Where the report is sent

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Location settings
LATITUDE = -5
LONGITUDE = 120
OPEN_METEO_URL = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m"
)


def fetch_current_temperature():
    """
    Fetches the current temperature data from Open-Meteo.
    """
    try:
        response = requests.get(OPEN_METEO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        temperature = current.get("temperature_2m")
        observed_time = current.get("time", "unknown time")

        if temperature is None:
            raise ValueError("No current temperature data found in API response.")

        return temperature, observed_time

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch weather data from Open-Meteo: {e}")
    except (ValueError, KeyError) as e:
        raise RuntimeError(f"Unexpected API response format: {e}")


def build_email_body(temperature):
    """Builds the friendly plain-text email body with IST timestamp."""
    ist = timezone(timedelta(hours=5, minutes=30))
    current_ist_time = datetime.now(ist).strftime("%d %b %Y, %I:%M %p IST")

    body = (
        f"Hello Praveen,\n\n"
        f"Here is your daily weather update for {current_ist_time}:\n\n"
        f"• Location: Latitude {LATITUDE}, Longitude {LONGITUDE}\n"
        f"• Current Temperature: {temperature}°C\n\n"
        f"The latest weather data was retrieved successfully from Open-Meteo.\n\n"
        f"Have a great and productive day ahead!"
    )
    return body


def send_email(temperature):
    """Sends the weather report email via Gmail SMTP."""
    ist = timezone(timedelta(hours=5, minutes=30))
    current_ist_date = datetime.now(ist).strftime("%d %b %Y")
    subject = f"Daily Weather Update ({current_ist_date}) - {temperature}°C"
    body = build_email_body(temperature)

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

        print("Success: Weather report email was sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check your Gmail address "
              "and App Password.")
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email due to an SMTP issue: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while sending the email: {e}")


def main():
    try:
        temperature, observed_time = fetch_current_temperature()
        print(f"Fetched latest temperature: {temperature}°C (at {observed_time})")
        send_email(temperature)

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
