# Kaggle Notebook Score Monitor

This small tool monitors Kaggle competition notebooks via API and sends Bark notifications when a new top notebook appears (sorted by score).

Files:
- `monitor_kaggle.py` - main monitoring script
- `requirements.txt` - Python dependencies
- `.env.example` - example environment file

Bark test script
----------------

You can test sending a push notification to an iPhone using Bark with the included `bark_test.py` script.

Set your Bark device key in an environment variable (`BARK_KEY` or `BARK_DEVICE_KEY`) or pass it with `--key`.

Examples:

```
# dry run (won't send):
python bark_test.py --key YOUR_DEVICE_KEY --title "Hello" --body "Test" --dry-run

# actually send:
python bark_test.py --key YOUR_DEVICE_KEY --title "Hello" --body "Real test"

# use .env file with BARK_KEY=... and run
python bark_test.py --title "From .env" --body "Hello"
```

Optional parameters: `--icon`, `--sound`, `--copy`, `--url` to set Bark-specific options.

## Setup

1. **Install dependencies:**
   pip install -r requirements.txt

2. **Set up Kaggle API:**
   - Go to [Kaggle Account Settings](https://www.kaggle.com/account) and create a new API token (downloads `kaggle.json`)
   - Place `kaggle.json` in `~/.kaggle/kaggle.json` (Linux/macOS) or `C:\Users\<USERNAME>\.kaggle\kaggle.json` (Windows)
   - Or set environment variables `KAGGLE_USERNAME` and `KAGGLE_KEY`

3. **Set up Bark notifications:**
   - Create a `.env` file or pass `--bark` directly
   - `BARK_KEY=your_bark_key_here`

## How It Works

The script fetches kernels/notebooks for the specified competition using the Kaggle API, sorted by score descending. Since precise scores may not be publicly available, it monitors changes in the top-ranked notebook. When a new notebook becomes the top-ranked one, a Bark notification is sent.

## Usage

- **Run once:**
  python monitor_kaggle.py --competition hull-tactical-market-prediction --once

- **Run continuously (poll every 5 minutes):**
  python monitor_kaggle.py --competition hull-tactical-market-prediction

Scheduling:
- Windows: use Task Scheduler to run the script periodically
- Linux/macOS: use cron or systemd timers

Notes & Caveats:
- The script uses the Kaggle CLI to fetch notebook data sorted by score. Actual score values may not be visible if not logged in as participant.
- Notifications trigger when the top notebook changes, as an indicator of new higher scores.
- Respects Kaggle API rate limits and requires authentication via `kaggle.json` or env vars.
