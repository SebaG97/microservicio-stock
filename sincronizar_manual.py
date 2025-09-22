"""
Ejecutar sincronización manual para probar los nuevos campos
"""
from servicios.sincronizador_automatico import SincronizadorAutomatico

def sincronizar_manual():
    """Ejecutar sincronización manual"""
    print("🔄 INICIANDO SINCRONIZACIÓN MANUAL...")
    
    try:
        # Crear instancia del sincronizador
        sincronizador = SincronizadorAutomatico()
        
        # Ejecutar sincronización
        resultado = sincronizador.sincronizar_partes_trabajo()
        
        print("\n✅ SINCRONIZACIÓN COMPLETADA:")
        print(f"  Partes nuevos: {resultado['partes_nuevos']}")
        print(f"  Partes actualizados: {resultado['partes_actualizados']}")
        print(f"  Técnicos nuevos: {resultado['tecnicos_nuevos']}")
        print(f"  Horas calculadas: {resultado['horas_calculadas']}")
        print(f"  Errores: {resultado['errores']}")
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")

if __name__ == "__main__":
    sincronizar_manual()
