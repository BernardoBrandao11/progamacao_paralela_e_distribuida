# Trabalho Final - Programação Paralela e Distribuída (URI Erechim)

Fiz um Merge Sort paralelo usando multiprocessing, com Barreira e Semaforo pra sincronizar. Explico aqui embaixo o que é, como rodar e uns perrengues que tive no caminho.

## Ideia geral

Peguei um cadastro de 800 mil veículos (`veiculos_desordenados.csv`) todo fora de ordem e mandei ordenar pelo preço usando Merge Sort. Rodei uma vez sequencial (jeito normal, um núcleo só) e uma vez paralelo (vários processos ao mesmo tempo, usando os núcleos todos do PC), só pra comparar o tempo e ver se compensa mesmo.

Obs: o csv que eu tinha no começo nem era um CSV de verdade, kkkk. Era um arquivo do Numbers que alguém salvou com extensão .csv errada, dava erro na hora de ler. Tive que fazer um script (`gerar_dataset.py`) que inventa um dataset de carro (marca, modelo, ano, km, preço, essas coisas) só pra ter dado real de verdade pra testar.

## Por que processo e não thread

Isso aqui é meio clássico: em Python, thread não adianta pra ganhar velocidade quando a tarefa é pesada de processamento (tipo ordenar um monte de coisa), porque tem uma trava interna do Python (o GIL) que só deixa UMA thread rodar código por vez, não importa quantos núcleos o PC tenha. Então threading nesse caso ia ser inútil.

Por isso usei `multiprocessing` em vez de `threading`: cada processo é tipo um Python inteiro rodando sozinho, sem essa trava compartilhada, então dá pra usar todos os núcleos ao mesmo tempo de verdade. E o legal é que o multiprocessing tem as mesmas ferramentas de sincronização que a gente vê com threads (Semaphore, Barrier, Lock), só que valendo entre processos.

## Como o algoritmo funciona

- Separa os dados em pedaços, um pedaço pra cada processo.
- Cada processo ordena o pedaço dele sozinho (isso sim roda em paralelo de verdade).
- Tem um **Semaphore** que limita quantos processos conseguem entregar o resultado deles ao mesmo tempo (é só pra simular um recurso limitado, tipo banda de memória).
- Tem uma **Barrier** que trava todo mundo até TODO processo terminar de ordenar e entregar seu pedaço. Ninguém passa da barreira sozinho.
- Depois que libera a barreira, o processo principal junta tudo (merge) e monta a lista final ordenada.

## O perrengue que tive que resolver

Na primeira versão que eu fiz, o merge final também rolava entre os processos (ia mesclando de dois em dois, tipo uma arvorezinha), passando os dados por uma lista compartilhada do `multiprocessing.Manager`. Só que isso é lento pra caramba quando o dado é "pesado" (cada linha do csv é um dicionário com um monte de campo), porque toda vez que os processos trocam essa lista entre si o Python tem que serializar tudo de novo.

Testei com os dados reais e tomei um susto: a versão "paralela" tava mais lenta que a sequencial! Speedup de 0.11x, ou seja, quase 10 vezes PIOR usando vários núcleos do que usando um só. Ridículo.

O que eu fiz pra resolver:
- Os processos passaram a ordenar só `(preço, índice)` em vez de carregar a linha inteira do csv o tempo todo - bem mais leve de trocar entre processos. Só no final eu recupero a linha completa usando o índice.
- Tirei aquele merge em árvore entre processos (que ficava indo e voltando um monte pela lista compartilhada) e troquei por um merge só, feito de uma vez no processo principal, depois que a barreira solta todo mundo.

Com isso o speedup foi de 0.85x pra uns 1.4x com os 800 mil registros. Bem melhor. E continua dando o mesmo resultado que o sequencial, só que mais rápido agora.

## Números que eu medi

Testei num Mac com 10 núcleos, ordenando os 800 mil veículos:

| Workers | Sequencial | Paralelo | Speedup |
|---|---|---|---|
| 2  | 1.17s | 1.13s | 1.04x |
| 4  | 1.18s | 0.83s | 1.42x |
| 6  | 1.19s | 0.81s | 1.47x |
| 8  | 1.21s | 0.84s | 1.43x |
| 10 | 1.19s | 0.87s | 1.38x |

O programa sempre confere se o resultado do paralelo bate certinho com o do sequencial antes de mostrar o speedup, então da pra confiar que ordenou certo.

Repara que o speedup não sobe na mesma proporção que o número de workers - isso é normal, tem um custo fixo de criar processo e passar dado entre eles que não some (lei de Amdahl, isso caiu na aula). Nessa máquina com esse tanto de dado o ponto bom fica em uns 4-6 workers, depois disso o ganho começa a cair de novo.

## Como rodar

Só precisa de Python 3, não tem nenhuma lib externa pra instalar.

Pra gerar o dataset de novo (não precisa, já vem pronto):

```bash
python3 gerar_dataset.py
```

Pra ordenar o csv de veículo pelo preço:

```bash
python3 Main -i veiculos_desordenados.csv -k preco -w 6
```

Dá pra ordenar por outra coluna também, tipo km:

```bash
python3 Main -i veiculos_desordenados.csv -k km
```

E tem um modo de teste sem csv, só pra ordenar N número aleatório:

```bash
python3 Main -n 2000000 -w 8
```

### Argumentos da CLI

| Flag | O que faz | Padrão |
|---|---|---|
| `-n, --size` | quantos elementos ordenar (modo sem csv) | 500000 |
| `-w, --workers` | quantos processos usar | núcleos que o PC tem |
| `-s, --merge-slots` | capacidade do semaforo | `workers // 2` |
| `--seed` | semente aleatoria (modo sem csv) | 42 |
| `-q, --quiet` | não fica printando o log de cada worker | desligado |
| `-i, --input` | csv real pra ordenar | nenhum |
| `-k, --key` | coluna do csv usada pra ordenar | `preco` |
| `-o, --output` | onde salva o csv ordenado | `saida_ordenada.csv` |

## Arquivos

- `Main` - o código, com o merge sort sequencial, o paralelo, e a CLI.
- `gerar_dataset.py` - o script que gera o `veiculos_desordenados.csv`.
- `veiculos_desordenados.csv` - os 800 mil veículos fora de ordem.
- `saida_ordenada.csv` - aparece depois de rodar o `Main` com `-i`, é o resultado ordenado.
