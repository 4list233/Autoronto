# API Timeout Issue - Resolution

## Problem
The Executive Dashboard was experiencing `ReadTimeout` errors when fetching data from the TeamGantt API in "live" mode:
```
HTTPSConnectionPool(host='api.teamgantt.com', port=443): Read timed out. (read timeout=30)
```

## Root Cause
- Dashboard was set to "live" mode (`data_source: "live"` in `config.json`)
- Every page load triggered a fresh API call to TeamGantt
- TeamGantt API occasionally takes longer than 30 seconds to respond
- No retry logic or fallback mechanism was in place

## Solutions Implemented

### 1. **Automatic Retry Logic with Exponential Backoff**
- Added `get_session_with_retries()` function in `api_client.py`
- Automatically retries failed requests up to 3 times
- Uses exponential backoff (1s, 2s, 4s between retries)
- Retries on connection errors, timeouts, and HTTP 5xx errors
- Retries on HTTP 429 (rate limiting)

### 2. **Increased Timeouts**
- Increased timeout for `fetch_children_hierarchical()` from 30s to 60s
- Increased timeout for `fetch_children_flat()` from 30s to 60s
- Other endpoints remain at 30s (sufficient for smaller responses)

### 3. **In-Memory Caching with TTL**
- Added in-memory cache for API responses
- Default TTL (Time-To-Live): 300 seconds (5 minutes)
- Configurable via `cache_ttl_seconds` in `config.json`
- Reduces API calls during page navigation
- Cache persists during the Streamlit session

### 4. **Graceful Fallback to Cached Files**
- If API call fails (timeout, network error, etc.), automatically falls back to cached JSON files
- Cached files are located in `data/` directory:
  - `children_hierarchical_4336931.json`
  - `children_flat_4336931.json`
  - `project_4336931.json`
- Displays warning message in console: "⚠️ API fetch failed: [error]. Falling back to cached data..."

### 5. **Cache Management**
- Added `clear_cache()` function to manually clear in-memory cache
- Cache is automatically cleared when Streamlit app restarts

## Configuration

Added new config option in `dashboard/config.json`:
```json
{
  "cache_ttl_seconds": 300,  // Cache API responses for 5 minutes
  "data_source": "live"      // or "cached"
}
```

## Recommended Settings

### For Development/Testing
```json
{
  "data_source": "cached",
  "cache_ttl_seconds": 300
}
```
- Use cached data for faster page loads
- Manually sync data when needed via Settings page

### For Production/Demos
```json
{
  "data_source": "live",
  "cache_ttl_seconds": 300
}
```
- Use live data for real-time updates
- 5-minute cache reduces API load during presentations
- Automatic fallback ensures dashboard stays operational even if API is slow/down

### For Presentations (Winter Workshop)
```json
{
  "data_source": "cached",
  "cache_ttl_seconds": 300
}
```
- Use cached data to avoid live API dependency
- Sync data shortly before presentation
- Guaranteed fast page loads with no network delays

## Testing the Fix

1. **Test API timeout handling:**
   ```bash
   cd /Users/5425855/Desktop/Uoft\ Studying/Autoronto
   source .venv/bin/activate
   streamlit run dashboard/app.py
   ```
   - Navigate to Executive Dashboard
   - If API is slow, you should see retry attempts in the logs
   - Dashboard should eventually load (either from API or fallback to cache)

2. **Test cache behavior:**
   - Set `data_source: "live"` in config.json
   - Load Executive Dashboard (triggers API call)
   - Navigate to another page and back (uses cache, no API call)
   - Wait 5+ minutes, reload (triggers new API call)

3. **Test fallback to cached data:**
   - Temporarily disconnect from internet
   - Try loading dashboard - should load from cached files

## Files Modified

1. `dashboard/utils/api_client.py`
   - Added retry logic and session management
   - Increased timeouts
   
2. `dashboard/utils/data_loader.py`
   - Added in-memory caching with TTL
   - Added fallback to cached files on error
   - Added `clear_cache()` function

3. `dashboard/config.json`
   - Added `cache_ttl_seconds` configuration

## Benefits

- **Reliability**: Dashboard works even when API is slow or unavailable
- **Performance**: In-memory cache reduces API calls and speeds up navigation
- **Flexibility**: Can switch between live and cached modes based on needs
- **User Experience**: No more timeout errors disrupting presentations
- **API-Friendly**: Reduces load on TeamGantt API with intelligent caching

## Notes

- Cached files in `data/` directory are your backup
- Keep them updated by running sync from Settings page
- In-memory cache is session-specific (cleared on app restart)
- File cache persists across restarts
