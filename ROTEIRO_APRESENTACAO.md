# Roteiro de Apresentação (Divisão de Falas — 3 Integrantes)

> **Tempo recomendado pelo edital:** 10 a 15 minutos de apresentação + até 5 minutos de perguntas.  
> **Meta de tempo sugerida:** ~12 minutos (aproximadamente **4 minutos por integrante**), deixando margem segura para a demonstração ao vivo.  
> **Regra importante do edital:** *Todos os integrantes são responsáveis pelo conhecimento global do projeto e devem estar aptos a responder perguntas sobre qualquer parte.*

---

## Visão Geral da Divisão

| Integrante | Papel Principal na Apresentação | Foco Técnico | Tempo Estimado |
| :--- | :--- | :--- | :--- |
| **Integrante 1** | Contextualização, Base de Dados e **Tabela Hash** | Problema, arquitetura geral, dataset e busca $O(1)$ com colisões | ~4 min |
| **Integrante 2** | **Lista Duplamente Encadeada** e **Grafo Ponderado** | Histórico de reprodução, fórmula de similaridade e Lista de Adjacência | ~4 min |
| **Integrante 3** | **Motor de Recomendação**, Explicabilidade e **Demonstração ao Vivo** | Integração das 3 estruturas, casos-limite, testes e limitações/melhorias | ~4 min |

---

## Parte 1 — Integrante 1 (~4 minutos)
**Tópicos:** Problema, Solução Proposta, Base de Dados e Tabela Hash.

### 1.1 Abertura e Contextualização do Problema (~1 min)
- **O que falar:**
  - Apresentar o grupo e o tema: **Sistema de Recomendação de Músicas baseado em similaridade sonora e histórico de reprodução**.
  - Explicar o problema: plataformas de streaming possuem catálogos gigantescos e precisam localizar faixas instantaneamente, registrar o que o usuário ouve em ordem e sugerir músicas coerentes sem parecer algo aleatório.
  - Mostrar o diagrama de arquitetura geral (CSV $\rightarrow$ Tabela Hash + Lista Encadeada + Grafo $\rightarrow$ Motor de Recomendação $\rightarrow$ Terminal).

### 1.2 Base de Dados e Estratégia de Filtragem (~1 min)
- **O que falar:**
  - Explicar a origem dos dados: dataset público do Spotify (Kaggle), originalmente com mais de 100 mil faixas.
  - Justificar a **filtragem estratificada** para 1.000 músicas: 10 gêneros distintos $\times$ 100 músicas mais populares de cada gênero.
  - Explicar por que não usamos banco de dados externo: o CSV atua como armazenamento permanente e as nossas estruturas em memória atuam como o motor de indexação e consulta, dando controle total sobre o que é avaliado na disciplina.

### 1.3 Tabela Hash — Implementação e Análise (~2 min)
- **O que falar:**
  - Mostrar o módulo `tabela_hash.py` (implementado do zero, sem usar o `dict` do Python como estrutura principal).
  - Justificar a escolha da **chave**: usamos o `id` único da música (e não o título), evitando conflitos entre músicas diferentes com o mesmo nome.
  - Explicar a função de espalhamento (hash polinomial) e o tratamento de colisões por **encadeamento separado** (buckets com listas de nós).
  - Apresentar a complexidade: **$O(1)$ no caso médio** para inserção e busca, e **$O(n)$ no pior caso** se muitas chaves colidirem no mesmo bucket.
  - Citar os números reais coletados no sistema (tamanho da tabela, fator de carga $\alpha$ e quantidade de colisões registradas na carga das 1.000 músicas).

> **Transição para o Integrante 2:** *"Com o catálogo indexado na Tabela Hash, precisamos agora guardar o que o usuário está ouvindo e conectar músicas parecidas. Passo a palavra para o [Nome do Integrante 2]."*

---

## Parte 2 — Integrante 2 (~4 minutos)
**Tópicos:** Lista Duplamente Encadeada (Histórico) e Grafo Ponderado (Similaridade).

### 2.1 Lista Duplamente Encadeada — Histórico de Reprodução (~1 min 30s)
- **O que falar:**
  - Mostrar o módulo `lista_encadeada.py` com a classe `NoHistorico` (guardando música, ordem de reprodução e ponteiros `anterior` e `proximo`).
  - Justificar por que uma Lista Duplamente Encadeada faz sentido: o histórico cresce dinamicamente conforme o usuário ouve músicas; inserimos no final em **$O(1)$** e conseguimos recuperar as últimas $N$ faixas ouvidas percorrendo de trás para frente em **$O(N)$**, sem precisar reorganizar a estrutura.
  - Destacar que o histórico não é apenas visual: ele participa ativamente do cálculo das próximas recomendações.

### 2.2 Grafo Ponderado — Modelagem e Matemática (~2 min 30s)
- **O que falar:**
  - Mostrar o módulo `grafo.py`: cada **vértice** é uma música e cada **aresta ponderada** representa o grau de afinidade entre duas faixas.
  - Justificar a escolha de **Lista de Adjacência** em vez de Matriz de Adjacência: para 1.000 músicas, uma matriz alocaria $1.000 \times 1.000 = 1.000.000$ de posições (quase todas vazias). Como conectamos cada música apenas às suas **Top-10 mais semelhantes**, a Lista de Adjacência armazena cerca de 10.000 arestas, economizando muita memória e acelerando a busca de vizinhos.
  - Explicar a **fórmula de afinidade (0 a 100)**:
    1. Calculamos a distância Euclidiana entre as 3 características sonoras (`energia`, `dancabilidade` e `valencia`).
    2. Convertemos a distância em similaridade sonora $\frac{1}{1 + D(A,B)}$ (até 60 pontos).
    3. Somamos bônus de contexto: **+25 pontos** se for o mesmo gênero e **+15 pontos** se for o mesmo artista.
  - Mostrar um exemplo visual nos slides (uma música central conectada às suas vizinhas com os respectivos pesos).

> **Transição para o Integrante 3:** *"Agora que temos busca rápida, histórico cronológico e conexões ponderadas, o [Nome do Integrante 3] vai mostrar como o motor une tudo isso, explica o motivo de cada sugestão e roda o sistema ao vivo."*

---

## Parte 3 — Integrante 3 (~4 minutos)
**Tópicos:** Motor de Recomendação, Demonstração ao Vivo, Casos-Limite e Conclusão.

### 3.1 Motor de Recomendação e Explicabilidade (~1 min)
- **O que falar:**
  - Explicar o fluxo completo em `motor_recomendacao.py`:
    1. Recupera as últimas faixas da **Lista Encadeada**.
    2. Consulta os vizinhos de cada uma no **Grafo**.
    3. Combina as pontuações de afinidade, remove músicas que o usuário já ouviu e ordena o Top-5.
  - Destacar o diferencial do projeto — **Explicabilidade sem IA**: usando os componentes do peso da aresta, o sistema gera justificativas claras (ex.: *"92% de afinidade: mesmo gênero (Pop), energia muito próxima e dançabilidade semelhante"*).

### 3.2 Demonstração ao Vivo no Terminal (~2 min)
- **Roteiro prático ao vivo (seguir exatamente nesta ordem para não perder tempo):**
  1. Abrir o terminal e iniciar o programa (`python main.py`).
  2. **Caso-limite 1 (Histórico vazio):** Tentar pedir recomendações antes de ouvir qualquer música e mostrar que o sistema trata o erro de forma amigável.
  3. **Busca e Reprodução:** Buscar uma música (ex.: Pop ou Rock), mostrar a busca instantânea pela Tabela Hash e registrar no histórico.
  4. **Recomendação + Explicabilidade:** Ouvir mais 1 ou 2 músicas e gerar a recomendação baseada no histórico, lendo em voz alta a tabela com a porcentagem de afinidade e a justificativa de uma das recomendações.
  5. **Caso-limite 2 (Música inexistente):** Digitar um nome que não existe para mostrar a mensagem de erro tratada e as sugestões parecidas.
  6. **Painel Técnico:** Abrir rapidamente a opção de inspeção para mostrar as colisões da Tabela Hash e o tamanho do Grafo em execução.

### 3.3 Testes, Limitações e Melhorias Futuras (~1 min)
- **O que falar:**
  - Comentar os **testes automatizados** (`pytest`) cobrindo colisões na Hash, lista vazia, IDs duplicados na carga do CSV e vértices isolados no Grafo.
  - Apontar **limitações atuais** com transparência: base estática de 1.000 músicas, falta de filtragem colaborativa (comparar gostos entre usuários diferentes) e histórico salvo apenas em memória durante a sessão.
  - Propor **melhorias futuras**: persistência do histórico do usuário em arquivo/JSON, interface web (ex.: Streamlit) com visualização interativa do grafo e inclusão de mais atributos musicais (como BPM/tempo).

---

## Dicas para a Sessão de Perguntas (Até 5 minutos)

Possíveis perguntas do professor e como qualquer integrante deve responder:

1. **"Por que não usaram o `dict` do Python ou a biblioteca `networkx`?"**
   - *Resposta:* Usamos implementação própria em `src/estruturas/` justamente para dominar e demonstrar a lógica interna (função hash, tratamento de colisões por encadeamento, ponteiros da lista e lista de adjacência do grafo), atendendo ao requisito da disciplina.
2. **"O que acontece se duas músicas tiverem o mesmo título no CSV?"**
   - *Resposta:* Como a chave da Tabela Hash é o `id` único da faixa, ambas são armazenadas sem sobrescrever uma à outra. Na busca por título, a interface lista as opções encontradas e resolve para o `id` escolhido.
3. **"Por que usar Lista de Adjacência e não Matriz de Adjacência no Grafo?"**
   - *Resposta:* Porque nosso grafo é esparso (cada música conecta apenas com as Top-10 mais similares). Uma matriz para 1.000 vértices gastaria espaço $O(V^2)$ com 1 milhão de células majoritariamente vazias, enquanto a lista de adjacência gasta $O(V + E)$.
4. **"Qual a complexidade do algoritmo de recomendação?"**
   - *Resposta:* Para as últimas $N$ músicas do histórico (ex.: $N=3$) e $K=10$ vizinhos por vértice no grafo, a coleta de candidatos é $O(N \cdot K)$ e a ordenação do pequeno conjunto de candidatos é $O(C \log C)$, executando em milissegundos.
