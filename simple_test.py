import requests
import json

# Hacer una prueba simple del endpoint
data = {
    "producto_id": 2,
    "deposito_origen_id": 2,
    "deposito_destino_id": 5,
    "cantidad": 1
}

response = requests.post(
    "http://localhost:8000/api/stock/movimientos/transferencia/",
    json=data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")