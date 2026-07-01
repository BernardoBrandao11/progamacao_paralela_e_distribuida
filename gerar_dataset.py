import csv
import random

SEED = 7
N = 800_000
ARQUIVO_SAIDA = "veiculos_desordenados.csv"

MARCAS_MODELOS = {
    "Volkswagen": ["Gol", "Polo", "Virtus", "T-Cross", "Nivus", "Saveiro"],
    "Chevrolet": ["Onix", "Tracker", "S10", "Cruze", "Spin", "Montana"],
    "Fiat": ["Argo", "Mobi", "Toro", "Strada", "Pulse", "Cronos"],
    "Toyota": ["Corolla", "Hilux", "Yaris", "Corolla Cross", "SW4"],
    "Hyundai": ["HB20", "Creta", "Tucson", "HB20S"],
    "Honda": ["Civic", "HR-V", "City", "Fit"],
    "Renault": ["Kwid", "Sandero", "Duster", "Logan"],
    "Jeep": ["Renegade", "Compass", "Commander"],
    "Ford": ["Ka", "EcoSport", "Ranger"],
    "Nissan": ["Kicks", "Versa", "Frontier"],
}
CORES = ["Branco", "Prata", "Preto", "Cinza", "Vermelho", "Azul", "Verde"]
COMBUSTIVEIS = ["Flex", "Gasolina", "Diesel", "Hibrido"]


def gerar_linhas(n, ano_atual=2026):
    linhas = []
    for i in range(n):
        marca = random.choice(list(MARCAS_MODELOS.keys()))
        modelo = random.choice(MARCAS_MODELOS[marca])
        ano = random.randint(2008, ano_atual)
        idade = max(0, ano_atual - ano)
        km = max(0, int(random.gauss(idade * 12_000, 8_000)))
        preco_base = random.uniform(45_000, 320_000)
        depreciacao = 1 - min(0.75, idade * 0.045)
        preco = round(preco_base * depreciacao + random.uniform(-5000, 5000), 2)
        preco = max(15_000.0, preco)
        linhas.append({
            "id": i + 1,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "km": km,
            "cor": random.choice(CORES),
            "combustivel": random.choice(COMBUSTIVEIS),
            "preco": preco,
        })
    return linhas


def main():
    random.seed(SEED)
    linhas = gerar_linhas(N)
    random.shuffle(linhas)

    campos = ["id", "marca", "modelo", "ano", "km", "cor", "combustivel", "preco"]
    with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"Gerados {N} registros em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
