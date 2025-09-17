#!/bin/bash

echo "🚀 Starting Railway deployment initialization..."

# Verificar conexión a base de datos
echo "📊 Testing database connection..."
python manage.py dbshell --command="SELECT 1;" || echo "⚠️  Database connection test failed, but continuing..."

# Crear migraciones si es necesario
echo "📝 Creating migrations..."
python manage.py makemigrations --noinput

# Aplicar migraciones
echo "🔄 Applying migrations..."
python manage.py migrate --noinput

# Verificar que las tablas se crearon
echo "🔍 Checking if tables were created..."
python manage.py dbshell --command="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';" || echo "⚠️  Could not list tables"

# Crear superusuario
echo "👤 Creating superuser..."
python create_superuser.py

# Poblar datos iniciales
echo "📊 Populating initial data..."
python populate_initial_data.py

echo "✅ Railway initialization completed!"
echo "🌐 Starting web server..."

# Iniciar servidor
exec gunicorn tvservices.wsgi:application --bind 0.0.0.0:$PORT --workers 2
