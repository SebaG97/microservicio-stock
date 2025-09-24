import requests

# Probar validación de depósitos iguales
response = requests.post(
    "http://localhost:8001/api/stock/movimientos/transferencia/",
    params={
        "producto_id": 2,
        "deposito_origen_id": 2,
        "deposito_destino_id": 2,
        "cantidad": 1
    }
)

print(f"Status Code: {response.status_code}")
if response.status_code == 400:
    error = response.json()
    print(f"✅ Validación exitosa - Error: {error.get('detail')}")
else:
    print(f"❌ No funcionó la validación: {response.text}")