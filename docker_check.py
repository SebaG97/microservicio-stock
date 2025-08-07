#!/usr/bin/env python3
import subprocess
import sys

print("=== DIAGNÓSTICO DOCKER POSTGRESQL ===")

try:
    # Ver contenedores corriendo
    print("1. Contenedores PostgreSQL corriendo:")
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    postgres_containers = [line for line in lines if 'postgres' in line.lower()]
    
    if postgres_containers:
        for container in postgres_containers:
            print(f"   ✅ {container}")
    else:
        print("   ❌ No hay contenedores PostgreSQL corriendo")
        
        # Ver contenedores parados
        print("\n2. Contenedores PostgreSQL parados:")
        result_all = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
        lines_all = result_all.stdout.split('\n')
        postgres_stopped = [line for line in lines_all if 'postgres' in line.lower()]
        
        if postgres_stopped:
            for container in postgres_stopped:
                print(f"   🔄 {container}")
            print("\n   💡 Puedes iniciar con: docker start <nombre_contenedor>")
        else:
            print("   ❌ No hay contenedores PostgreSQL")

    # Ver puertos en uso
    print("\n3. Puertos 5432-5435 en uso:")
    for port in [5432, 5433, 5434, 5435]:
        result_port = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if f":{port}" in result_port.stdout:
            print(f"   ✅ Puerto {port} en uso")
        else:
            print(f"   ❌ Puerto {port} libre")

except Exception as e:
    print(f"Error ejecutando comandos: {e}")

print("\n=== FIN DIAGNÓSTICO ===")
