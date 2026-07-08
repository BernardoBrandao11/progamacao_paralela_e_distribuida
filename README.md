O trabalho pedia dois algoritmos de ordenação rodando em paralelo, um deles bolha. Fiz um **Bubble Sort** e um **Merge Sort**, os dois com `multiprocessing`, usando Barrier, Semaphore e Lock pra sincronizar.

## Ideia geral

Peguei um cadastro de 800 mil veículos (`veiculos_desordenados.csv`) fora de ordem e mandei ordenar pelo preço. Pra cada algoritmo rodo uma vez sequencial e uma vez paralelo, confiro se o resultado bate e comparo o tempo.

Em Python thread não ajuda em tarefa pesada por causa do GIL (só uma thread roda por vez). Por isso usei `multiprocessing`: cada processo roda sozinho, sem essa trava, usando todos os núcleos de verdade.

## Como funciona

Nos dois algoritmos a ideia é a mesma: divide os dados em blocos, um por processo. Cada processo ordena o seu bloco sozinho (merge sort num caso, bubble sort no outro). Um Semaphore controla quantos processos publicam o resultado ao mesmo tempo, uma Barrier trava todo mundo até acabar, e no final o processo principal junta os blocos ordenados.

## Perrengues

No merge sort, a primeira versão trocava a linha inteira do csv entre os processos toda hora, e isso deu **speedup de 0.11x** (mais lento que sequencial!) por causa do custo de serializar tanto dado. Resolvi trocando só `(preço, índice)` entre os processos e fazendo o merge final de uma vez só. Foi pra uns 1.4x.

No bubble sort tentei primeiro o jeito clássico (odd-even transposition, sincronizando a cada comparação): 6 mil elementos levaram **224 segundos**, um desastre. Troquei pra dividir em blocos como o merge sort, e caiu pra menos de 1 segundo.

## Números

Mac com 10 núcleos, dados reais dos 800 mil veículos (bolha usa amostra de 20 mil, porque é O(n²) e não escala pro dataset inteiro):

| Workers | Merge (speedup) | Bolha (speedup) |
|---|---|---|
| 2  | 1.06x | 5.05x |
| 4  | 1.46x | 15.84x |
| 6  | 1.53x | 27.91x |
| 8  | 1.51x | 35.35x |
| 10 | 1.41x | 38.36x |

O merge sort segura por volta de 4-6 workers, depois cai (custo de criar processo). O bubble sort sobe bem mais rápido que o número de workers porque é O(n²) - dividir em `p` pedaços divide o trabalho por `p²`.

## Como rodar

```bash
python3 Main -i veiculos_desordenados.csv -k preco -w 6
```

Só um dos dois algoritmos:

```bash
python3 Main -i veiculos_desordenados.csv -a bubble
python3 Main -i veiculos_desordenados.csv -a merge
```

Sem csv, com números aleatórios:

```bash
python3 Main -n 2000000 -w 8 -a merge
```

Flags principais: `-a` (bubble/merge/both), `-w` (workers), `-i` (csv de entrada), `-k` (coluna chave), `-n` (tamanho no modo aleatório).

## Arquivos

- `Main` - os dois algoritmos + CLI.
- `gerar_dataset.py` - gera o `veiculos_desordenados.csv`.
- `saida_ordenada.csv` - resultado, gerado ao rodar com `-i`.