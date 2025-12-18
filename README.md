# smSpy — Automated Anonymous Social Media OSINT Bot

**smSpy** is a Python-based OSINT Telegram bot that allows anonymous extraction of publicly available data from **Instagram**, **TikTok**, and **Spotify**.  
The project combines browser automation (Selenium) with Telegram bot interaction to provide a simple, menu-driven OSINT tool.

> [!WARNING]
> The developer takes no responsibility for any actions performed using this tool.
>  
> You use it entirely at your own risk and are responsible for complying with local laws and platform terms of service.

## Features

- Fetch avatars from **TikTok**, **Instagram**, and **Spotify**
- View and download **TikTok Stories**
- View **TikTok reposts**
- View and download **Instagram Stories**
- Download **full Instagram profiles**
- Extract **Spotify playlist covers**

## Usage Principles

- Fully anonymous — **no login required**
- No authorization in social networks
- OSINT-based data extraction
- Works only with publicly available data

## How It Works

- Uses **Selenium (Chrome WebDriver)** to open public profile pages
- Automatically bypasses basic popups and consent banners
- Parses required data directly from page source
- Sends extracted media back to the user via **Telegram**
- All interactions are handled through an inline-button menu

## Technologies Used

- Python 3.8+
- `python-telegram-bot`
- Selenium (Chrome WebDriver)
- Requests
- Regular Expressions

## Requirements

Before running the bot, ensure you have:

- **Python 3.8+**
- **Google Chrome**
- **ChromeDriver** (matching your Chrome version)
- Installed dependencies:
  - `python-telegram-bot`
  - `selenium`
  - `requests`

---

This project also provides a Python script that automatically opens **Instagram** and **TikTok** anonymous story-viewer websites in two separate browser windows using **Selenium**, applies a custom **click animation**, bypasses cookie consent buttons, enters usernames, and keeps the pages open for viewing.

Both viewers run **in parallel** using Python threads.

## Features
- Automatically launches:
  - **Anonymous Instagram * Story Viewer** (`third-party tool`*)
  - **TikTok * Story Viewer** (`third-party tool`*)
- Custom red **click-animation indicator** injected into the page.
- Automatically clicks cookie-banner buttons:
  - *"Отказаться"* (Russian “Reject”) on Instagram*
  - *"Do not consent"* on TikTok*  
- Types the username into the active input field.
- Opens both viewers **simultaneously** using multithreading.
- Keeps browser tabs open for 5 minutes (300 seconds).

## Requirements
Before running the script, ensure you have:

- **Python 3.8+**
- Google **Chrome** installed
- The following Python packages:
  - `selenium`
  - `webdriver-manager`

Install dependencies with:

```
pip install selenium webdriver-manager
```

## Usage

1. Open `main.py`
2. Run it:
```
python main.py
```
3. Enter the requested usernames when prompted:
  - Ig username
  - TT username
```
Enter Instagram username: example_ig
Enter TikTok username: example_tt
```
Two automated Chrome windows will open and begin processing.

## Additional Files

1. **`ig.py`** — automation for actions on the Instagram* site separately.
2. **`tt.py`** — automation for actions on the TikTok* site separately.

---

> [!WARNING]
> This script is intended for educational and personal automation purposes only.
> 
> Using automated tools may violate terms of service of third-party websites*.
>
> Use responsibly and at your own risk.
