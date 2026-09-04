#!/bin/bash

echo "🚀 Building for Vercel..."

# Install PostgreSQL client for psycopg2 compilation
echo "📦 Installing PostgreSQL client..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations if database URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️ Running database migrations..."
    python manage.py migrate --noinput || echo "⚠️ Migrations failed, continuing..."
fi

echo "✅ Build complete!"
