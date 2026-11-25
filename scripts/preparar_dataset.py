"""Prepara o dataset estratificado de 1.000 músicas a partir da base do Spotify (Kaggle)."""

from pathlib import Path
import kagglehub
import pandas as pd

GENEROS_ALVO = [
    "pop",
    "rock",
    "hip-hop",
    "mpb",
    "electronic",
    "indie",
    "metal",
    "sertanejo",
    "r-n-b",
    "reggaeton",
]
MUSICAS_POR_GENERO = 100

COLUNAS_ORIGEM = {
    "track_id": "id",
    "track_name": "titulo",
    "artists": "artista",
    "track_genre": "genero",
    "energy": "energia",
    "danceability": "dancabilidade",
    "valence": "valencia",
    "popularity": "popularidade",
}


def localizar_dataset_bruto() -> Path:
    """Localiza o dataset.csv no cache local do kagglehub ou faz o download."""
    cache_dir = Path.home() / ".cache" / "kagglehub" / "datasets" / "maharshipandya" / "-spotify-tracks-dataset" / "versions"
    if cache_dir.exists():
        for versao in sorted(cache_dir.iterdir(), reverse=True):
            candidato = versao / "dataset.csv"
            if candidato.exists():
                return candidato

    pasta = Path(kagglehub.dataset_download("maharshipandya/-spotify-tracks-dataset"))
    arquivo = pasta / "dataset.csv"
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo dataset.csv não encontrado em {pasta}")
    return arquivo


def preparar_dataset(origem: Path, destino: Path) -> pd.DataFrame:
    """Filtra 100 músicas mais populares por gênero, sem IDs duplicados."""
    df = pd.read_csv(origem, usecols=list(COLUNAS_ORIGEM.keys()))
    df = df.rename(columns=COLUNAS_ORIGEM)

    # Remove linhas com campos essenciais ausentes ou vazios
    df = df.dropna(subset=list(COLUNAS_ORIGEM.values()))
    for col_texto in ("id", "titulo", "artista", "genero"):
        df[col_texto] = df[col_texto].astype(str).str.strip()
        df = df[df[col_texto] != ""]

    # Garante faixa válida [0.0, 1.0] para métricas sonoras
    for col_num in ("energia", "dancabilidade", "valencia"):
        df = df[(df[col_num] >= 0.0) & (df[col_num] <= 1.0)]

    df["popularidade"] = df["popularidade"].astype(int)

    selecionadas = []
    ids_vistos: set[str] = set()

    for genero in GENEROS_ALVO:
        sub = (
            df[df["genero"] == genero]
            .sort_values(by=["popularidade", "id"], ascending=[False, True])
        )
        # Remove IDs já escolhidos em gêneros anteriores ou duplicados no mesmo gênero
        sub_unico = sub[~sub["id"].isin(ids_vistos)].drop_duplicates(subset=["id"])
        top_n = sub_unico.head(MUSICAS_POR_GENERO)

        if len(top_n) < MUSICAS_POR_GENERO:
            raise ValueError(
                f"Gênero '{genero}' possui apenas {len(top_n)} faixas únicas (esperado: {MUSICAS_POR_GENERO})."
            )

        ids_vistos.update(top_n["id"].tolist())
        selecionadas.append(top_n)

    resultado = pd.concat(selecionadas, ignore_index=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(destino, sep=";", index=False, encoding="utf-8")
    return resultado


def main() -> None:
    raiz = Path(__file__).resolve().parent.parent
    destino = raiz / "dados" / "musicas_1000.csv"
    origem = localizar_dataset_bruto()
    df_final = preparar_dataset(origem, destino)

    print(f"Dataset salvo em: {destino}")
    print(f"Total de músicas: {len(df_final)}")
    print(f"IDs únicos: {df_final['id'].nunique()}")
    print("\nDistribuição por gênero:")
    print(df_final["genero"].value_counts().to_string())


if __name__ == "__main__":
    main()
