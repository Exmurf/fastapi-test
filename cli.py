import sys

import requests


if len(sys.argv) < 2:
    print("Kullanım: python cli.py <isim>")
    sys.exit(1)

name = sys.argv[1]

response = requests.get(
    f"http://127.0.0.1:8000/hello/{name}",
    timeout=10,
)

response.raise_for_status()

data = response.json()

print(data["message"])