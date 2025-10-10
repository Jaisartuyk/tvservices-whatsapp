"""
Script para limpiar archivos que no pertenecen al proyecto tvservices_project
Elimina:
1. Carpeta security_management/ (pertenece a otro proyecto)
2. Plantillas HTML de empacadora de camarón
3. Archivos CSS relacionados con empacadora

Autor: Cascade AI
Fecha: 2025-10-10
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Archivos y carpetas a eliminar
ITEMS_TO_DELETE = [
    # Carpeta completa de security_management
    "security_management",
    
    # Plantillas HTML de empacadora de camarón
    "plantilla_pistoleo_mejorada.html",
    "lista_reportes_mejorada.html",
    "home_profesional.html",
    "dashboard_moderno.html",
    "reporte_auditoria_mejorado.html",
    
    # Archivos CSS de empacadora
    "estilos_reporte.css",
]

def create_backup_log():
    """Crea un log con los archivos que serán eliminados"""
    log_file = BASE_DIR / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("LIMPIEZA DE PROYECTO TVSERVICES - LOG DE ELIMINACIÓN\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("ARCHIVOS Y CARPETAS A ELIMINAR:\n")
        f.write("-" * 80 + "\n")
        
        for item in ITEMS_TO_DELETE:
            item_path = BASE_DIR / item
            if item_path.exists():
                if item_path.is_dir():
                    size = sum(f.stat().st_size for f in item_path.rglob('*') if f.is_file())
                    f.write(f"📁 {item} (Carpeta - {size:,} bytes)\n")
                else:
                    size = item_path.stat().st_size
                    f.write(f"📄 {item} ({size:,} bytes)\n")
            else:
                f.write(f"⚠️  {item} (No encontrado)\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    return log_file

def delete_items():
    """Elimina los archivos y carpetas especificados"""
    deleted_count = 0
    not_found_count = 0
    error_count = 0
    
    print("🧹 INICIANDO LIMPIEZA DEL PROYECTO TVSERVICES")
    print("=" * 80)
    
    for item in ITEMS_TO_DELETE:
        item_path = BASE_DIR / item
        
        try:
            if item_path.exists():
                if item_path.is_dir():
                    # Eliminar carpeta completa
                    shutil.rmtree(item_path)
                    print(f"✅ Eliminada carpeta: {item}")
                    deleted_count += 1
                else:
                    # Eliminar archivo
                    item_path.unlink()
                    print(f"✅ Eliminado archivo: {item}")
                    deleted_count += 1
            else:
                print(f"⚠️  No encontrado: {item}")
                not_found_count += 1
                
        except Exception as e:
            print(f"❌ Error al eliminar {item}: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE LIMPIEZA:")
    print(f"   ✅ Eliminados: {deleted_count}")
    print(f"   ⚠️  No encontrados: {not_found_count}")
    print(f"   ❌ Errores: {error_count}")
    print("=" * 80)
    
    return deleted_count, not_found_count, error_count

def main():
    """Función principal"""
    print("\n" + "🔍 ANÁLISIS DE ARCHIVOS A ELIMINAR")
    print("=" * 80)
    
    # Crear log de backup
    log_file = create_backup_log()
    print(f"✅ Log de backup creado: {log_file.name}")
    print()
    
    # Mostrar resumen
    print("📋 ARCHIVOS Y CARPETAS QUE SERÁN ELIMINADOS:")
    print("-" * 80)
    for item in ITEMS_TO_DELETE:
        item_path = BASE_DIR / item
        if item_path.exists():
            if item_path.is_dir():
                print(f"   📁 {item}/")
            else:
                print(f"   📄 {item}")
    print()
    
    # Confirmar eliminación
    response = input("⚠️  ¿Deseas continuar con la eliminación? (si/no): ").strip().lower()
    
    if response in ['si', 's', 'yes', 'y']:
        print()
        deleted, not_found, errors = delete_items()
        
        if errors == 0:
            print("\n✨ ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
            print(f"📝 Revisa el log para más detalles: {log_file.name}")
        else:
            print("\n⚠️  Limpieza completada con algunos errores.")
            print(f"📝 Revisa el log para más detalles: {log_file.name}")
    else:
        print("\n❌ Operación cancelada por el usuario.")
        print(f"📝 Log guardado en: {log_file.name}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
