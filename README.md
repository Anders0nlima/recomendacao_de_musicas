# Sistema de Recomendação de Músicas — Estruturas de Dados

Aplicação em Python desenvolvida para a disciplina de **Estruturas de Dados** (Prof. Lídio Campos), que recomenda músicas com base em similaridade sonora e histórico de reprodução, utilizando **Tabela Hash**, **Lista Duplamente Encadeada** e **Grafo Ponderado** implementados do zero.

---

## 1. Problema e Objetivos

Plataformas de streaming musical lidam com catálogos extensos e precisam responder rapidamente a três necessidades centrais:
1. **Localizar faixas instantaneamente** por identificador único;
2. **Registrar o histórico de reprodução** em ordem cronológica e recuperar as faixas mais recentes;
3. **Recomendar novas músicas coerentes** com o gosto do usuário, explicando o motivo de cada sugestão.

Este projeto resolve esse problema em memória utilizando estruturas de dados clássicas integradas a um motor de recomendação explicável, sem depender de bancos de dados externos ou modelos de IA.

---

## 2. Estruturas de Dados Utilizadas (Implementação Própria)

Todas as estruturas centrais estão isoladas em [src/estruturas/](file:///c:/Projetos/recomendacao_de_musicas/src/estruturas/) e foram codificadas sem bibliotecas que escondam seu funcionamento interno:

| Estrutura | Arquivo | Papel no Sistema | Complexidade Principal |
| :--- | :--- | :--- | :--- |
| **Tabela Hash** (Encadeamento Separado) | [tabela_hash.py](file:///c:/Projetos/recomendacao_de_musicas/src/estruturas/tabela_hash.py) | Indexa as 1.000 músicas por `id` único para busca rápida e bloqueio de duplicatas | Inserção e Busca: $O(1)$ médio / $O(n)$ pior caso |
| **Lista Duplamente Encadeada** | [lista_encadeada.py](file:///c:/Projetos/recomendacao_de_musicas/src/estruturas/lista_encadeada.py) | Armazena o histórico cronológico (`inicio`, `fim`, `anterior`, `proximo`) | Inserção no fim: $O(1)$ / Últimas $N$ faixas: $O(N)$ |
| **Grafo Ponderado** (Lista de Adjacência) | [grafo.py](file:///c:/Projetos/recomendacao_de_musicas/src/estruturas/grafo.py) | Conecta cada música às suas **Top-10** mais semelhantes com peso de 0 a 100 | Consulta de vizinhos: $O(K \log K)$, com $K \le 10$ |

### Métricas Reais Observadas com `musicas_1000.csv`
- **Tabela Hash:** capacidade de `1301` buckets, `1000` elementos, fator de carga `0.7686`, `299` colisões tratadas por encadeamento separado e maior cadeia de tamanho `5`.
- **Grafo Ponderado:** `1000` vértices, `10000` arestas direcionadas, grau médio `10.0` e `0` vértices isolados.

---

## 3. Cálculo de Afinidade e Explicabilidade

Entre duas músicas $A$ e $B$, calculamos a distância Euclidiana sobre três atributos normalizados em $[0, 1]$ (`energia`, `dancabilidade` e `valencia`):

$$D(A, B) = \sqrt{(E_A - E_B)^2 + (D_A - D_B)^2 + (V_A - V_B)^2}$$

A similaridade sonora é convertida para:

$$\text{SimAudio}(A, B) = \frac{1}{1 + D(A, B)} \in (0, 1]$$

O **peso da aresta (0 a 100)** combina:
- Até **60 pontos** pela similaridade sonora ($60 \times \text{SimAudio}$);
- **+25 pontos** se ambas forem do mesmo gênero;
- **+15 pontos** se compartilharem o mesmo artista.

A partir desses componentes, o [motor_recomendacao.py](file:///c:/Projetos/recomendacao_de_musicas/src/motor_recomendacao.py) gera justificativas legíveis (ex.: *"Mesmo artista"*, *"Mesmo gênero musical"*, *"Nível de energia muito próximo"*), combina os vizinhos das últimas músicas do histórico com fator de recência e remove faixas que o usuário já ouviu.

---

## 4. Casos-Limite Tratados

- Tentativa de pedir recomendações ou visualizar histórico com a **Lista Encadeada vazia**;
- **Busca por música inexistente** (exibe mensagem amigável e sugere títulos parecidos);
- **ID duplicado** ao inserir na Tabela Hash ou carregar o CSV;
- **Vértice isolado** no Grafo (sem vizinhos conectados);
- **Entradas inválidas** no menu do terminal (letras, números fora de faixa ou interrupção via teclado).

---

## 5. Como Instalar e Executar

### Pré-requisitos
- Python 3.11+ instalado.

### Passo a Passo
1. Instale as dependências de apoio:
   ```bash
   pip install -r requirements.txt
   ```
2. *(Opcional)* O arquivo tratado [dados/musicas_1000.csv](file:///c:/Projetos/recomendacao_de_musicas/dados/musicas_1000.csv) já está incluído no repositório. Caso queira regerá-lo a partir do dataset do Kaggle:
   ```bash
   python scripts/preparar_dataset.py
   ```
3. Execute a aplicação:
   ```bash
   python main.py
   ```
4. Execute os testes automatizados:
   ```bash
   pytest -v
   ```

---

## 6. Estrutura do Projeto

```text
recomendacao_de_musicas/
├── dados/musicas_1000.csv          # Base estratificada (10 gêneros x 100 faixas)
├── scripts/preparar_dataset.py     # Filtro e limpeza do dataset bruto
├── src/
│   ├── modelos.py                  # Dataclass Musica
│   ├── carregador.py               # Leitura do CSV e carga inicial
│   ├── motor_recomendacao.py       # Integração e explicabilidade
│   ├── cli.py                      # Interface no terminal com Rich
│   └── estruturas/
│       ├── tabela_hash.py          # Tabela Hash com encadeamento separado
│       ├── lista_encadeada.py      # Lista Duplamente Encadeada (histórico)
│       └── grafo.py                # Grafo Ponderado (lista de adjacência)
├── tests/                          # Suíte de testes unitários e de integração (21 testes)
├── main.py                         # Ponto de entrada
├── requirements.txt                # Dependências de apoio
├── PLANO_DE_IMPLEMENTACAO.md       # Plano incremental do projeto
├── ROTEIRO_APRESENTACAO.md         # Divisão de falas para os 3 integrantes
└── README.md                       # Documentação principal
```

---

## 7. Fontes, Bibliotecas e Materiais Consultados

- **Dataset:** *Spotify Tracks Dataset* (Maharshi Pandya, Kaggle — `maharshipandya/-spotify-tracks-dataset`).
- **Bibliotecas de apoio (apenas interface, testes e preparo do CSV):**
  - `rich` — formatação de tabelas e painéis no terminal;
  - `pytest` — execução dos testes automatizados;
  - `pandas` e `kagglehub` — download e filtragem inicial do CSV bruto.
- **Referências teóricas:** Materiais da disciplina de Estruturas de Dados (Prof. Lídio Campos) sobre Tabelas de Dispersão, Listas Encadeadas e Grafos. 
