#!/usr/bin/env bash
set -e

# ==============================================================================
# EventGenie AI - One-Command Google Cloud Run Deployment
# ==============================================================================

echo "========================================================"
echo "  🚀 EventGenie AI: Deploying to Google Cloud Run"
echo "========================================================"

SERVICE_NAME="eventgenie-ai"
REGION="${GCP_REGION:-us-central1}"

# Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: Google Cloud SDK ('gcloud') is not installed or not in PATH."
    echo "   Please install gcloud: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo "📍 Target Project: $PROJECT_ID"
echo "📍 Target Region:  $REGION"

# Prompt for Gemini API Key if not set in environment
if [ -z "$GEMINI_API_KEY" ]; then
    read -s -p "Enter your Gemini API Key (from Google AI Studio): " GEMINI_API_KEY
    echo ""
fi

# Enable necessary Google Cloud APIs
echo "⚙️ Enabling Cloud Run, Cloud Build, and Artifact Registry APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# Deploy directly from source
echo "📦 Building container image & deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},GEMINI_MODEL=gemini-2.5-flash,ENVIRONMENT=production" \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10

echo ""
echo "========================================================"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)')
echo "🎉 SUCCESS: EventGenie AI is live on Cloud Run!"
echo "🔗 Access your application: $SERVICE_URL"
echo "========================================================"
