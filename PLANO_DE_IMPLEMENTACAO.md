# Plano de Implementação Incremental — Sistema de Recomendação de Músicas

> **Disciplina:** Estruturas de Dados (Prof. Lídio Campos)  
> **Objetivo:** Desenvolver uma aplicação em Python que recomenda músicas com base em similaridade sonora e histórico de reprodução, utilizando **Tabela Hash**, **Lista Duplamente Encadeada** e **Grafo Ponderado** implementados do zero.

---

## 1. Visão Geral da Arquitetura

A aplicação funciona 100% em memória RAM após o carregamento de um arquivo CSV estático (simulando o armazenamento em disco), sem necessidade de banco de dados externo:

```text
[ CSV (dados/musicas_1000.csv) ]
               │
               ▼  (Carga inicial + validação de IDs duplicados)
┌─────────────────────────────────────────────────────────────┐
│                   ESTRUTURAS EM MEMÓRIA                     │
│                                                             │
│  1. TabelaHash (chave: id_musica)                           │
│     └─ Busca e inserção em O(1) médio (encadeamento sep.)   │
│                                                             │
│  2. ListaEncadeada (histórico de reprodução)                │
│     └─ Armazena ordem cronológica e últimas faixas ouvidas  │
│                                                             │
│  3. GrafoPonderado (lista de adjacência, Top-K vizinhos)    │
│     └─ Conecta músicas por afinidade sonora + gênero/artista│
└─────────────────────────────────────────────────────────────┘
               │
               ▼
[ Motor de Recomendação + Explicabilidade ]
               │
               ▼
[ Interface CLI no Terminal (biblioteca Rich) ]
```

### Decisões Técnicas e Melhorias sobre a Ideia Inicial

| Ponto | Decisão Adotada | Justificativa |
| :--- | :--- | :--- |
| **Chave da Tabela Hash** | `id` único da música (em vez do título) | Evita ambiguidade entre músicas com o mesmo nome ou versões diferentes. A busca por título na interface filtra os registros e resolve para o `id`, que é então consultado em $O(1)$ na Tabela Hash. |
| **Fórmula de Similaridade** | Distância Euclidiana usando `energia`, `dancabilidade` e `valencia` | Aproveita todas as métricas numéricas do dataset, tornando o cálculo matematicamente sólido. |
| **Regra de Conexão do Grafo** | Top-$K$ vizinhos mais próximos ($K = 10$) por pontuação híbrida | Evita que o grafo fique desconexo entre gêneros parecidos (ex.: Pop e Indie), mantendo o grafo esparso e justificando o uso de **Lista de Adjacência** em vez de Matriz de Adjacência. |
| **Lista Encadeada** | Lista **Duplamente Encadeada** (`inicio` e `fim`) | Permite inserir no fim em $O(1)$ e recuperar as últimas $N$ músicas ouvidas percorrendo de trás para frente em $O(N)$, alimentando diretamente o motor de recomendação. |
| **Interface** | Terminal (CLI) estilizado com `rich` | Elimina riscos de compatibilidade na apresentação em sala e foca 100% nas estruturas de dados e na explicabilidade das recomendações. |

---

## 2. Estrutura de Pastas Planejada

```text
recomendacao_de_musicas/
├── dados/
│   └── musicas_1000.csv          # Base tratada com 1.000 músicas (10 gêneros x 100 faixas)
├── scripts/
│   └── preparar_dataset.py       # Script auxiliar para filtrar o dataset bruto do Kaggle
├── src/
│   ├── __init__.py
│   ├── modelos.py                # Classe Musica (dataclass/objeto com atributos da faixa)
│   ├── estruturas/
│   │   ├── __init__.py
│   │   ├── tabela_hash.py        # Tabela Hash com encadeamento separado (implementação própria)
│   │   ├── lista_encadeada.py    # Lista Duplamente Encadeada para histórico (implementação própria)
│   │   └── grafo.py              # Grafo Ponderado com lista de adjacência (implementação própria)
│   ├── motor_recomendacao.py     # Cálculo de afinidade, combinação com histórico e justificativas
│   └── cli.py                    # Menu interativo no terminal com Rich e tratamento de entradas
├── tests/
│   ├── test_tabela_hash.py       # Testes unitários de colisões, busca, remoção e duplicatas
│   ├── test_lista_encadeada.py   # Testes de lista vazia, inserção e últimas ouvidas
│   ├── test_grafo.py             # Testes de vértices isolados, pesos e vizinhos Top-K
│   └── test_motor.py             # Testes de integração e remoção de músicas já ouvidas
├── main.py                       # Ponto de entrada da aplicação
├── requirements.txt              # Dependências externas de apoio (ex.: rich, pytest)
└── README.md                     # Instruções de execução, arquitetura e fontes consultadas
```

> **Atenção à regra do edital:** Nenhuma biblioteca pronta (`dict` como tabela hash principal, `collections.deque` ou `networkx`) deve substituir as estruturas em `src/estruturas/`. Elas serão codificadas do zero com nós, ponteiros/referências e buckets explícitos.

---

## 3. Etapas Incrementais de Implementação

### Etapa 1 — Setup do Projeto e Preparação da Base de Dados
**Objetivo:** Ter o ambiente Python configurado e o arquivo `dados/musicas_1000.csv` limpo, validado e pronto para consumo.

1. Criar `requirements.txt` com `rich` e `pytest`, além da estrutura inicial de pastas.
2. Baixar o dataset do Spotify (Kaggle) e verificar os nomes exatos das colunas disponíveis (`track_id`, `track_name`, `artists`, `track_genre`, `popularity`, `energy`, `danceability`, `valence`).
3. Implementar `scripts/preparar_dataset.py` para:
   - Selecionar **10 gêneros bem definidos** (ex.: `pop`, `rock`, `hip-hop`, `mpb`, `electronic`, `indie`, `metal`, `sertanejo`, `r-n-b`, `reggaeton`).
   - Remover registros com valores nulos ou IDs duplicados.
   - Ordenar por `popularidade` decrescente e extrair as **100 faixas mais populares de cada gênero** (total: 1.000 músicas).
   - Exportar `dados/musicas_1000.csv` padronizado com separador `;` e colunas:
     `id;titulo;artista;genero;energia;dancabilidade;valencia;popularidade`.
4. **Critério de conclusão:** Arquivo `musicas_1000.csv` gerado com exatamente 1.000 linhas válidas, valores numéricos entre `0.0` e `1.0`, e zero IDs repetidos.

---

### Etapa 2 — Modelo de Dados e Tabela Hash (`tabela_hash.py`)
**Objetivo:** Indexar o catálogo de músicas em memória com busca em $O(1)$ médio e tratamento explícito de colisões.

1. Criar `src/modelos.py` com a classe `Musica` (`id`, `titulo`, `artista`, `genero`, `energia`, `dancabilidade`, `valencia`, `popularidade`).
2. Implementar `TabelaHash` em `src/estruturas/tabela_hash.py`:
   - Vetor interno de *buckets* com tamanho inicial primo (ex.: `1009` ou `1301` para manter fator de carga $\alpha < 0{,}8$ com 1.000 músicas).
   - **Tratamento de colisões:** Encadeamento separado (cada bucket é uma lista encadeada de nós `(chave, valor)`).
   - **Função de espalhamento (`_hash`):** Polinomial sobre os caracteres do `id` da música (`soma = (soma * 31 + ord(c)) % capacidade`).
   - **Operações obrigatórias:**
     - `inserir(id_musica, musica)`: bloqueia/sinaliza erro ao tentar inserir chave duplicada e contabiliza colisões ocorridas.
     - `buscar(id_musica)`: retorna a `Musica` ou `None` (caso não exista).
     - `remover(id_musica)`: remove o nó do bucket correspondente e retorna booleano indicando sucesso.
     - `obter_estatisticas()`: retorna total de elementos, capacidade, fator de carga ($\alpha$) e número de colisões (excelente dado para exibir na apresentação).
3. **Critério de conclusão:** `tests/test_tabela_hash.py` passando, cobrindo inserção, busca, remoção, chave inexistente, chave duplicada e colisão forçada.

---

### Etapa 3 — Lista Duplamente Encadeada (`lista_encadeada.py`)
**Objetivo:** Gerenciar o histórico de reprodução fictício do usuário de forma eficiente e rastreável.

1. Implementar `NoHistorico` (`musica`, `ordem`, `timestamp`, `anterior`, `proximo`).
2. Implementar `ListaHistorico` em `src/estruturas/lista_encadeada.py`:
   - Ponteiros `inicio`, `fim` e contador `tamanho`.
   - **Operações obrigatórias:**
     - `esta_vazia()`: retorna `True` se `tamanho == 0`.
     - `registrar_reproducao(musica)`: insere novo nó no `fim` em $O(1)$ com número de ordem sequencial.
     - `ultimas_musicas(quantidade)`: percorre a partir de `fim` usando `anterior` e retorna as últimas $N$ músicas ouvidas (sem duplicatas ou mantendo a mais recente).
     - `listar_historico()`: percorre do `inicio` ao `fim` (ou inverso) para exibição.
     - `contem_musica(id_musica)`: verifica se a faixa já foi ouvida pelo usuário.
     - `limpar()`: reinicia o histórico.
3. **Critério de conclusão:** `tests/test_lista_encadeada.py` passando, cobrindo histórico vazio, ordem de reprodução e recuperação das últimas $N$ faixas.

---

### Etapa 4 — Grafo Ponderado de Similaridade (`grafo.py`)
**Objetivo:** Modelar as relações de similaridade entre músicas usando Lista de Adjacência e pesos matemáticos bem definidos.

1. Definir a matemática da **Afinidade Total (0 a 100)**:
   - Distância Euclidiana sonora:
     $$D(A, B) = \sqrt{(E_A - E_B)^2 + (D_A - D_B)^2 + (V_A - V_B)^2}$$
   - Similaridade de áudio normalizada:
     $$\text{SimAudio}(A, B) = \frac{1}{1 + D(A, B)} \in (0, 1]$$
   - Peso da aresta (escala 0 a 100):
     - Até **60 pontos**: `60 * SimAudio(A, B)`
     - **+25 pontos**: se `A.genero == B.genero`
     - **+15 pontos**: se `A.artista == B.artista`
   - *Observação:* Peso maior indica **maior similaridade** (facilita o ranking decrescente).
2. Implementar `GrafoMusicas` em `src/estruturas/grafo.py`:
   - Representação por **Lista de Adjacência**: dicionário/estrutura mapeando `id_musica -> lista de Aresta(destino_id, peso, detalhes)`.
   - **Operações obrigatórias:**
     - `adicionar_vertice(id_musica)`
     - `adicionar_aresta(id_origem, id_destino, peso, detalhes)`
     - `construir_conexoes(musicas, k=10)`: para cada música, calcula a afinidade com as demais e mantém apenas as **Top-$K$ ($K=10$) conexões mais fortes** (garantindo grafo esparso e rápido).
     - `obter_vizinhos(id_musica)`: retorna as arestas ordenadas por peso decrescente; retorna lista vazia caso seja um vértice isolado.
3. **Critério de conclusão:** `tests/test_grafo.py` passando, validando cálculo de peso, limite de $K$ vizinhos, vértice inexistente e vértice isolado.

---

### Etapa 5 — Motor de Recomendação e Explicabilidade (`motor_recomendacao.py`)
**Objetivo:** Integrar Tabela Hash, Lista Encadeada e Grafo para gerar recomendações personalizadas e justificadas.

1. Implementar os dois modos de recomendação:
   - **Por música escolhida:** Busca a música na `TabelaHash`, registra no `ListaHistorico` (opcional/configurável) e consulta seus vizinhos no `GrafoMusicas`.
   - **Com base no histórico:**
     1. Verifica se `ListaHistorico.esta_vazia()` (caso positivo, retorna aviso amigável pedindo para ouvir ao menos 1 música).
     2. Recupera as últimas $N$ músicas ouvidas (ex.: 3 a 5).
     3. Para cada música do histórico, consulta seus vizinhos no Grafo e **agrega/combina as pontuações** (aplicando um fator de recência maior para a música mais recente ou média ponderada).
     4. Filtra e remove recomendações cujo `id` já está no histórico.
     5. Ordena do maior para o menor score e retorna o Top-5.
2. Implementar o **Gerador de Justificativa (Explicabilidade)**:
   - Analisa os componentes do peso entre a música de referência e a recomendada para montar frases claras:
     - Mesmo artista (`"Mesmo artista (Dua Lipa)"`)
     - Mesmo gênero (`"Mesmo gênero musical (Pop)"`)
     - Diferença em energia $\le 0{,}08$ (`"Nível de energia muito próximo"`)
     - Diferença em dançabilidade $\le 0{,}08$ (`"Dançabilidade semelhante"`)
     - Diferença em valência $\le 0{,}08$ (`"Clima/valência equivalente"`)
3. **Critério de conclusão:** `tests/test_motor.py` passando, garantindo que músicas já ouvidas não sejam recomendadas e que toda recomendação possua justificativa textual.

---

### Etapa 6 — Interface CLI, Casos-Limite e Carga Inicial (`cli.py` e `main.py`)
**Objetivo:** Criar uma experiência limpa no terminal, à prova de falhas durante a apresentação ao vivo.

1. Implementar o carregador de CSV em `main.py`:
   - Lê `dados/musicas_1000.csv`, instancia `Musica`, insere na `TabelaHash` (tratando e contabilizando eventuais IDs duplicados) e constrói o `GrafoMusicas`.
2. Implementar menu interativo no terminal com `rich`:
   - **Opção 1:** Buscar música por nome/artista e "Tocar" (registra na Lista Encadeada e exibe recomendações imediatas). Se não encontrar exatamente, sugerir títulos parecidos.
   - **Opção 2:** Ver histórico de reprodução (exibe a Lista Encadeada com ordem e detalhes).
   - **Opção 3:** Gerar recomendações baseadas no meu histórico (com tabela colorida mostrando `% de afinidade` e o bloco *"Por que recomendamos?"*).
   - **Opção 4:** Inspecionar estruturas de dados (painel técnico para a apresentação: estatísticas da Tabela Hash — buckets, fator de carga, colisões —, tamanho da Lista Encadeada e amostra de vizinhos de um vértice no Grafo).
   - **Opção 5:** Limpar histórico / Sair.
3. **Tratamento de casos-limite obrigatórios (Requisito 5 do edital):**
   - Entrada de menu inválida (letras em menu numérico, opções fora do intervalo).
   - Busca por música inexistente (sem crash, com sugestão de nomes próximos).
   - Solicitar recomendação com histórico vazio.
   - Música isolada no grafo (sem conexões).
   - Tentativa de inserir ID duplicado na Tabela Hash.

---

### Etapa 7 — Testes Finais, Documentação e Material de Apresentação
**Objetivo:** Fechar todos os entregáveis exigidos pelo edital para envio no SIGAA e apresentação presencial.

1. Executar toda a suíte de testes (`pytest`) e validar manualmente todos os fluxos no terminal.
2. Escrever `README.md` contendo:
   - Descrição do problema e objetivos.
   - Instruções passo a passo de instalação (`pip install -r requirements.txt`) e execução (`python main.py`).
   - Explicação das 3 estruturas de dados e suas complexidades (Big-O).
   - Fontes e referências (Dataset Kaggle/Spotify, biblioteca `rich`, livros/materiais da disciplina).
3. Preparar os **Slides de Apoio** (recomendado 8 a 10 slides objetivos) incluindo um diagrama visual do grafo mostrando uma música central conectada às suas vizinhas mais semelhantes.
4. Ensaiar a apresentação seguindo o roteiro dividido entre os 3 integrantes (`ROTEIRO_APRESENTACAO.md`).
