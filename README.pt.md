# Preço de apartamentos na Polônia (ago/2023 a jun/2024)

## Sobre
Pipeline que pega CSVs mensais de anúncios de apartamentos à venda na Polônia, limpa os dados com Python (pandas), carrega num PostgreSQL via Docker e responde perguntas de preço com SQL.

Principais passos:
- Junta 11 arquivos mensais (`apartments_pl_*.csv`) e marca cada linha com o mês de origem.
- Remove a coluna `condition` e duplicatas por `id`, mantendo o anúncio do mês mais recente.
- Calcula `price_per_m2` e marca como outlier quem fica acima de 2x ou abaixo de 0,5x da mediana da própria cidade.
- Gera `data/clean/apartments_clean.csv` (92.967 linhas, 32 colunas).
- O Docker sobe o Postgres 16, cria a tabela, carrega o CSV e cria as views, tudo sozinho.

Dados: [Apartment Prices in Poland](https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland) (Kaggle, de krzysztofjamroz), fotos mensais de anúncios de venda. Os CSVs originais não estão no repositório: baixe e coloque em `data/raw/`.

Ferramentas: Python (pandas, NumPy, scikit-learn), PostgreSQL 16, Docker Compose.

## Estrutura
```
data/raw/     CSVs originais (um por mês)
data/clean/   CSV limpo gerado pelo script
Python/       clean_apartments.py, gus.ipynb (salários), ml_warsaw.ipynb (modelo de preço) e notebooks de exploração
sql/          01_create_tables.sql, 02_load_data.sql, 03_views.sql
docker-compose.yml
```

## Como rodar
1. Instale as dependências: `pip install pandas numpy`
2. Gere o CSV limpo, de dentro da pasta `Python`:
   ```
   cd Python
   python clean_apartments.py
   ```
3. Na raiz do projeto, suba o banco (Docker Desktop aberto):
   ```
   docker compose up -d
   docker compose logs
   ```
   No log devem aparecer `COPY 92967` e três `CREATE VIEW`, sem `ERROR`.
4. Conecte no Postgres (pgAdmin ou psql): host `localhost`, porta `5434`, banco `poland_apartments`, usuário `postgres`, senha definida no `docker-compose.yml`.

Para recriar o banco do zero: `docker compose down -v` e depois `docker compose up -d`. Os scripts de `sql/` só rodam com o volume vazio.

## Views
- `v_median_price_by_city`: mediana do preço por m² em cada cidade, sem outliers.
- `v_warsaw_price_evolution`: mediana mensal do preço por m² em Varsóvia.
- `v_var_median`: a mesma série com o mês anterior (`LAG`) e a variação percentual mês a mês.

## Resultados
- Mediana do preço por m² (sem outliers): Varsóvia 16.779, Cracóvia 15.000, Gdańsk 13.184.
- Em Varsóvia, a mediana foi de 14.465 em ago/2023 para 17.917 em jun/2024, alta de 23,9%.
- A variação mensal ficou entre 0,86% e 4,43%, com os maiores saltos em dez/2023 e jan/2024.

## Preço × salário
O `Python/gus.ipynb` baixa o salário médio mensal bruto por powiat da API do Banco de Dados Local do GUS (BDL, variável 64428, 380 powiats, 4 páginas de 100), fica com as 15 cidades que aparecem nos apartamentos e junta com a mediana do preço por m².

`months_per_m2` = mediana do preço por m² / salário de 2024.

| Cidade | Mediana do m² (PLN) | Salário 2024 (PLN) | Meses de salário por m² |
|---|---|---|---|
| Varsóvia | 16.779 | 10.715 | 1,57 |
| Cracóvia | 15.000 | 10.455 | 1,43 |
| Breslávia | 12.392 | 9.425 | 1,31 |
| ... | | | |
| Katowice | 7.929 | 10.052 | 0,79 |
| Radom | 6.324 | 8.269 | 0,76 |

1 m² custa de 0,76 (Radom) a 1,57 (Varsóvia) salários mensais brutos. Katowice tem um dos maiores salários e um dos m² mais baratos, então fica perto do fim.

## Modelo de preço (Varsóvia)

Uma regressão linear (`ml_warsaw.ipynb`) prevê o preço anunciado a partir da área, da distância do centro e do ano de construção.

- R² no conjunto de teste: **0,72**
- Cada m² a mais: **+16.548 zł**
- Cada km a mais do centro: **−42.328 zł**
- Cada ano mais novo: **+1.831 zł**

Três variáveis explicam cerca de 72% da variação do preço. O resto vem do que os dados não têm, como acabamento, andar ou vista. Os preços são anunciados, não de venda.

## Limitações
- Os preços são de anúncios, não de vendas fechadas.
- A série cobre só 11 meses, então não dá para separar tendência de sazonalidade.
- Os salários do GUS são médias anuais e o valor de 2024 vale para todo o período dos preços (ago/2023 a jun/2024).
- Os arquivos de aluguel (`apartments_rent_*`) estão em `data/raw/`, mas ainda não entram no pipeline.

## Próximos passos
- Testar mais variáveis (andar, quartos, comodidades) e comparar com o modelo de 3 variáveis.
