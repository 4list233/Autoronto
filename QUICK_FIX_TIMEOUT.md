# Quick Fix for TeamGantt API Timeout

## Immediate Solution

If you're experiencing timeout errors right now:

### Option 1: Switch to Cached Mode (Fastest Fix)

Edit `dashboard/config.json` and change:

```json
{
  "data_source": "cached"
}
```

Then restart the dashboard:

```bash
cd /Users/5425855/Desktop/Uoft\ Studying/Autoronto/dashboard
streamlit run app.py
```

### Option 2: Use the Fixes Already Applied

The following improvements have already been implemented in your code:

1. **Automatic retry logic** - API calls retry 3 times with exponential backoff
2. **Increased timeouts** - 60 seconds for large data fetches (up from 30)
3. **In-memory caching** - API responses cached for 5 minutes
4. **Automatic fallback** - Falls back to cached files if API fails

Simply restart your Streamlit app and the fixes will take effect.

## What Changed

### Files Modified

1. `dashboard/utils/api_client.py` - Added retry logic and increased timeouts
2. `dashboard/utils/data_loader.py` - Added caching and fallback mechanisms
3. `dashboard/config.json` - Added `cache_ttl_seconds: 300`

### New Behavior

- **Live Mode**: Fetches from API, caches for 5 minutes, falls back to files on error
- **Cached Mode**: Always reads from local JSON files

## For Your Remote Server (pc4.in.autoronto.ca)

### Sync the Updated Code

```bash
# From your Mac
cd /Users/5425855/Desktop/Uoft\ Studying/Autoronto

rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '.DS_Store' \
  dashboard/utils/ \
  dashboard/config.json \
  autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/dashboard/

# SSH to the server
ssh autoronto@pc4.in.autoronto.ca

# Restart the service
sudo systemctl restart autoronto-dashboard

# Check status
sudo systemctl status autoronto-dashboard
```

## Recommended Configuration

### For Winter Workshop Presentation (Feb 17)

Use **cached mode** for reliability:

```json
{
  "data_source": "cached",
  "cache_ttl_seconds": 300
}
```

**Before the presentation:**
1. Go to Settings page in dashboard
2. Click "Sync Data from TeamGantt API"
3. Verify data is fresh in `data/` directory
4. Switch to cached mode

This ensures:
- No network delays during presentation
- No risk of API timeouts
- Instant page loads
- Guaranteed uptime

### For Daily Use

Use **live mode** with the new safety features:

```json
{
  "data_source": "live",
  "cache_ttl_seconds": 300
}
```

This provides:
- Real-time data (refreshed every 5 minutes)
- Automatic fallback if API is slow
- Reduced API load with smart caching

## Testing the Fix

### Test Locally

```bash
cd /Users/5425855/Desktop/Uoft\ Studying/Autoronto
source .venv/bin/activate
cd dashboard
streamlit run app.py
```

Navigate to Executive Dashboard and verify:
- Page loads without timeout
- If API is slow, you see retry attempts in console
- Falls back to cached data if needed

### Test on Remote Server

```bash
# Check logs
ssh autoronto@pc4.in.autoronto.ca
journalctl -u autoronto-dashboard -f

# Open in browser
open http://pm.in.autoronto.ca:8501
```

## Troubleshooting

### Still Getting Timeouts?

1. **Check cached data exists:**
   ```bash
   ls -la /Users/5425855/Desktop/Uoft\ Studying/Autoronto/data/
   ```
   You should see:
   - `children_hierarchical_4336931.json`
   - `children_flat_4336931.json`
   - `project_4336931.json`

2. **Switch to cached mode temporarily:**
   Edit `config.json`: `"data_source": "cached"`

3. **Check API token is valid:**
   ```bash
   cat .env | grep TEAMGANTT
   ```

### Dashboard Won't Start?

```bash
# Check for Python errors
cd /Users/5425855/Desktop/Uoft\ Studying/Autoronto
source .venv/bin/activate
python -c "from dashboard.utils import api_client, data_loader"
```

## Summary of Improvements

| Issue | Before | After |
|-------|--------|-------|
| Timeout | 30s fixed | 60s with 3 retries |
| API Failure | Crash | Fallback to cached |
| Page Navigation | Fresh API call | Cached 5 minutes |
| Network Error | Hard fail | Automatic retry |
| Rate Limiting | Fail immediately | Retry with backoff |

## Questions?

See `API_TIMEOUT_FIX.md` for detailed technical documentation.
