# smSpy - Automated Anonymus Instagram & TikTok Story Viewer  
This project provides a Python script that automatically opens **Instagram** and **TikTok** anonymous story-viewer websites in two separate browser windows using **Selenium**, applies a custom **click animation**, bypasses cookie consent buttons, enters usernames, and keeps the pages open for viewing.

Both viewers run **in parallel** using Python threads.

## Features
- Automatically launches:
  - **Anonymous Instagram Story Viewer** (`third-party tool*`)
  - **TikTok Story Viewer** (`third-party tool*`)
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
> Using automated tools may violate terms of service of third-party websites.
>
> Use responsibly and at your own risk.
