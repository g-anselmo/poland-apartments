# Preço de apartamentos na Polônia (ago/2023 a jun/2024)

## Sobre
Pipeline que pega CSVs mensais de anúncios de apartamentos à venda na Polônia, limpa os dados com Python (pandas), carrega num PostgreSQL via Docker e responde perguntas de preço com SQL.

Principais passos:
- Junta 11 arquivos mensais (`apartments_pl_*.csv`) e marca cada linha com o mês de origem.
- Remove a coluna `condition` e duplicatas por `id`, mantendo o anúncio do mês mais recente.
- Calcula `price_per_m2` e marca como outlier quem fica acima de 2x ou abaixo de 0,5x da mediana da própria cidade.
- Gera `data/clean/apartments_clean.csv` (92.967 linhas, 32 colunas).
- O Docker sobe o Postgres 16, cria a tabela, carrega o CSV e cria as views, tudo sozinho.

Ferramentas: Python (pandas, NumPy), PostgreSQL 16, Docker Compose.

## Estrutura
```
data/raw/     CSVs originais (um por mês)
data/clean/   CSV limpo gerado pelo script
Python/       clean_apartments.py e notebooks de exploração
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

## Limitações
- Os preços são de anúncios, não de vendas fechadas.
- A série cobre só 11 meses, então não dá para separar tendência de sazonalidade.
- Os arquivos de aluguel (`apartments_rent_*`) estão em `data/raw/`, mas ainda não entram no pipeline.

## Próximos passos
- Modelo de regressão simples com scikit-learn para Varsóvia.
- Comparar preço por m² com salário médio por região (dados do GUS).
