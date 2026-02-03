# CRM Backend Deployment Guide - Render

## Pre-Deployment Checklist ✅

### 1. Code Updates
- [x] Renamed `calendar` app to `calendar_events` (fixes Python built-in module conflict)
- [x] Updated all migrations and references
- [x] JWT token lifetime set to 30 days
- [x] Database credentials moved to environment variables (security fix)

### 2. Required Environment Variables for Render

Set these in your Render dashboard under Environment Variables:

```
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=crmbackend-xgc8.onrender.com,localhost,127.0.0.1
DATABASE_URL=your-neon-database-url
GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

### 3. Deployment Steps

#### Option A: Using Render Dashboard (Recommended)

1. **Push changes to GitHub**
   ```bash
   git add .
   git commit -m "Update: rename calendar app, fix DB config, JWT 30 days"
   git push
   ```

2. **Go to Render Dashboard** → Your Service → Settings
   - Scroll to "Build & Deploy"
   - Click "Deploy latest commit"

3. **Monitor deployment** in the Logs tab

#### Option B: Manual Render Deploy Button (if configured)

Just click the Render deploy button if you have one set up.

### 4. Post-Deployment Verification

1. **Check server status**
   ```
   https://crmbackend-xgc8.onrender.com/api/schema/
   ```

2. **Test API endpoints**
   - Swagger UI: `https://crmbackend-xgc8.onrender.com/api/docs/`
   - ReDoc: `https://crmbackend-xgc8.onrender.com/api/redoc/`

3. **Verify migrations ran**
   ```
   Check Render logs for "Running migrations" messages
   ```

### 5. Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| Calendar import error | ✅ Fixed by renaming `calendar` → `calendar_events` |
| DB credentials exposed | ✅ Fixed by using environment variables |
| JWT token lifetime | ✅ Set to 30 days in settings |
| Static files | ✅ Configured with WhiteNoise |

### 6. Rollback (if needed)

If deployment fails:
1. Go to Render Dashboard
2. Select the service
3. Click "Redeploy previous version"

### 7. Monitoring

- **Logs**: Render Dashboard → Logs tab
- **Database**: Monitor at Neon Console
- **API Health**: `https://crmbackend-xgc8.onrender.com/api/schema/`

---

## Files Changed in This Update

- `crmbackend/settings.py` - Database config + JWT settings
- `crmbackend/urls.py` - Updated calendar_events URL
- `Procfile` - Already correct (no changes needed)
- `requirement.txt` - All dependencies included
- `calendar_events/` - App renamed from `calendar/`
- `render.yaml` - New build configuration file (optional)

---

## Important Notes

⚠️ **DO NOT** commit this if you have secrets:
- Store `SECRET_KEY` in Render environment variables
- Store database credentials in `DATABASE_URL` environment variable
- Store API keys in environment variables

✅ **All done!** Your backend is ready for deployment.

