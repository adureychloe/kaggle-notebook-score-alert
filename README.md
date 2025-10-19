# Kaggle Notebook Score Monitor

This small tool monitors the Kaggle competition "Code" page and sends Bark notifications when a notebook with a higher score appears.

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

Usage:
1. Install dependencies:
   pip install -r requirements.txt

2. Create a `.env` file (or pass `--bark`):
   BARK_KEY=your_bark_key_here

3. Run once:
   python monitor_kaggle.py --competition hull-tactical-market-prediction --once

4. Run continuously (poll every 5 minutes):
   python monitor_kaggle.py --competition hull-tactical-market-prediction

Scheduling:
- Windows: use Task Scheduler to run the script periodically
- Linux/macOS: use cron or systemd timers

Notes & Caveats:
- This script scrapes the Kaggle page and may break if Kaggle changes their HTML.
- Kaggle may enforce rate limits or require authentication for detailed info; for heavy monitoring consider using Kaggle APIs if available.

