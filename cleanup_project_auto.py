"""
Script AUTOMÁTICO para limpiar archivos que no pertenecen al proyecto tvservices_project
Elimina sin confirmación:
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

def create_backup_log(deleted_items, not_found_items, errors):
    """Crea un log con los archivos eliminados"""
    log_file = BASE_DIR / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("LIMPIEZA DE PROYECTO TVSERVICES - LOG DE ELIMINACIÓN\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("✅ ARCHIVOS Y CARPETAS ELIMINADOS:\n")
        f.write("-" * 80 + "\n")
        for item in deleted_items:
            f.write(f"   {item}\n")
        
        if not_found_items:
            f.write("\n⚠️  NO ENCONTRADOS:\n")
            f.write("-" * 80 + "\n")
            for item in not_found_items:
                f.write(f"   {item}\n")
        
        if errors:
            f.write("\n❌ ERRORES:\n")
            f.write("-" * 80 + "\n")
            for item, error in errors:
                f.write(f"   {item}: {error}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"RESUMEN: {len(deleted_items)} eliminados, {len(not_found_items)} no encontrados, {len(errors)} errores\n")
        f.write("=" * 80 + "\n")
    
    return log_file

def delete_items():
    """Elimina los archivos y carpetas especificados"""
    deleted_items = []
    not_found_items = []
    errors = []
    
    print("🧹 INICIANDO LIMPIEZA AUTOMÁTICA DEL PROYECTO TVSERVICES")
    print("=" * 80)
    print()
    
    for item in ITEMS_TO_DELETE:
        item_path = BASE_DIR / item
        
        try:
            if item_path.exists():
                if item_path.is_dir():
                    # Contar archivos antes de eliminar
                    file_count = len(list(item_path.rglob('*')))
                    shutil.rmtree(item_path)
                    print(f"✅ Eliminada carpeta: {item}/ ({file_count} archivos)")
                    deleted_items.append(f"📁 {item}/ ({file_count} archivos)")
                else:
                    # Obtener tamaño antes de eliminar
                    size = item_path.stat().st_size
                    item_path.unlink()
                    print(f"✅ Eliminado archivo: {item} ({size:,} bytes)")
                    deleted_items.append(f"📄 {item} ({size:,} bytes)")
            else:
                print(f"⚠️  No encontrado: {item}")
                not_found_items.append(item)
                
        except Exception as e:
            print(f"❌ Error al eliminar {item}: {str(e)}")
            errors.append((item, str(e)))
    
    print()
    print("=" * 80)
    print("📊 RESUMEN DE LIMPIEZA:")
    print(f"   ✅ Eliminados: {len(deleted_items)}")
    print(f"   ⚠️  No encontrados: {len(not_found_items)}")
    print(f"   ❌ Errores: {len(errors)}")
    print("=" * 80)
    
    return deleted_items, not_found_items, errors

def main():
    """Función principal"""
    print("\n🔍 PROYECTO: tvservices_project")
    print("📍 Ubicación:", BASE_DIR)
    print()
    
    # Ejecutar limpieza
    deleted, not_found, errors = delete_items()
    
    # Crear log
    log_file = create_backup_log(deleted, not_found, errors)
    
    print()
    if len(errors) == 0:
        print("✨ ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
    else:
        print("⚠️  Limpieza completada con algunos errores.")
    
    print(f"📝 Log guardado en: {log_file.name}")
    print()
    
    # Mostrar archivos eliminados
    if deleted:
        print("📋 ARCHIVOS ELIMINADOS:")
        print("-" * 80)
        for item in deleted:
            print(f"   {item}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
