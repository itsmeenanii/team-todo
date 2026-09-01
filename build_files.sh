#!/bin/bash

echo "🚀 Building for Vercel..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️ Running database migrations..."
    python manage.py migrate --noinput
fi

echo "✅ Build complete!"
