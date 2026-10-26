# ==============================================================================
# EventGenie AI - One-Command Google Cloud Run Deployment (PowerShell)
# ==============================================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  🚀 EventGenie AI: Deploying to Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ServiceName = "eventgenie-ai"
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }

# Check gcloud CLI
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Google Cloud SDK ('gcloud') is not found in PATH." -ForegroundColor Red
    Write-Host "   Please install it: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Exit 1
}

$ProjectId = gcloud config get-value project 2>$null
if (-not $ProjectId -or $ProjectId -eq "(unset)") {
    $ProjectId = Read-Host "Enter your Google Cloud Project ID"
    gcloud config set project $ProjectId
}

Write-Host "📍 Target Project: $ProjectId" -ForegroundColor Green
Write-Host "📍 Target Region:  $Region" -ForegroundColor Green

$GeminiKey = $env:GEMINI_API_KEY
if (-not $GeminiKey) {
    $GeminiKey = Read-Host "Enter your Gemini API Key (from Google AI Studio)"
}

Write-Host "⚙️ Enabling Cloud Run and Cloud Build APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

Write-Host "📦 Building and deploying directly to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-env-vars "GEMINI_API_KEY=$GeminiKey,GEMINI_MODEL=gemini-2.5-flash,ENVIRONMENT=production" `
    --memory 1Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10

$ServiceUrl = gcloud run services describe $ServiceName --platform managed --region $Region --format 'value(status.url)'
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "🎉 SUCCESS: EventGenie AI is live on Cloud Run!" -ForegroundColor Green
Write-Host "🔗 Access your application: $ServiceUrl" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
