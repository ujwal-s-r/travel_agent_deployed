# Deployment Guide

## Required Environment Variables

Set these in your Railway dashboard (Variables tab):

- `mistral_api_key` - Your Mistral/Qubrid AI API key (get from https://platform.qubrid.com)

## APIs Used

- **Mistral LLM**: Requires API key (qubrid.com)
- **Weather**: Open-Meteo (free, no key needed)
- **Places**: OpenStreetMap Overpass API (free, no key needed)
- **Geocoding**: Nominatim (free, no key needed)

## Deployment Steps

1. Push code to GitHub
2. Connect Railway to your repository
3. Add `mistral_api_key` environment variable in Railway
4. Railway will auto-deploy

## Testing Deployment

Visit: `https://your-app.up.railway.app/health`

Should return:
```json
{
  "status": "healthy",
  "service": "Tourism AI Agent",
  "version": "1.0.0"
}
```
