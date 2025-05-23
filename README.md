# Exemplo de Airflow com DBT e Iceberg

Este projeto demonstra como usar o Apache Airflow para orquestrar transformações DBT em dados armazenados no formato Apache Iceberg.

### Visão Detalhada do Projeto

Este projeto integra várias tecnologias modernas de dados para criar um pipeline de processamento completo:

1. **Fluxo de Dados**:
   - Dados brutos são armazenados no MinIO (compatível com S3)
   - O Apache Iceberg fornece um formato de tabela que permite controle de versão e gerenciamento de esquema
   - O Trino consulta os dados usando o catálogo Iceberg
   - O DBT transforma os dados brutos em modelos de negócios
   - O Airflow orquestra todo o processo

2. **Componentes Principais**:
   - **Apache Airflow**: Plataforma de orquestração que gerencia a execução de tarefas em uma ordem específica. No projeto, o Airflow executa a inicialização de dados, criação de tabelas e transformações DBT.
   - **DBT (Data Build Tool)**: Ferramenta de transformação que permite escrever transformações em SQL e gerenciar dependências entre modelos. O projeto usa DBT para transformar dados brutos em modelos de negócios.
   - **Apache Iceberg**: Formato de tabela de código aberto que oferece controle de versão, evolução de esquema e otimizações de desempenho. O Iceberg é usado para armazenar os dados de forma eficiente.
   - **Trino**: Motor de consulta distribuído que permite consultar dados de várias fontes. No projeto, o Trino é usado para consultar dados no formato Iceberg.
   - **Hive Metastore**: Serviço que armazena metadados sobre tabelas e partições. É usado pelo Iceberg para rastrear metadados das tabelas.
   - **MinIO**: Armazenamento de objetos compatível com S3 que armazena os arquivos de dados físicos.

3. **Modelos de Dados**:
   - **Staging**: Modelos que limpam e padronizam os dados brutos
   - **Marts**: Modelos agregados que fornecem visões de negócios dos dados

4. **Benefícios desta Arquitetura**:
   - Separação clara entre armazenamento e computação
   - Controle de versão e evolução de esquema com Iceberg
   - Transformações modulares e testáveis com DBT
   - Orquestração flexível com Airflow
   - Infraestrutura totalmente containerizada com Docker

## Arquitetura

O projeto inclui os seguintes componentes:

- **Apache Airflow**: Orquestra o pipeline de dados
- **DBT (Data Build Tool)**: Gerencia transformações de dados
- **Apache Iceberg**: Fornece formato de tabela para armazenamento de dados
- **Trino**: Motor de consulta SQL que suporta Iceberg
- **Hive Metastore**: Armazena metadados para tabelas Iceberg
- **MinIO**: Armazenamento de objetos compatível com S3 para arquivos de dados

## Estrutura do Projeto

```
.
├── dags/                      # DAGs do Airflow
│   └── dbt_iceberg_dag.py     # DAG de exemplo que executa DBT no Iceberg
├── dbt_project/               # Projeto DBT
│   ├── models/                # Modelos DBT
│   │   ├── staging/           # Modelos de staging
│   │   │   ├── stg_products.sql
│   │   │   ├── stg_sales.sql
│   │   │   └── schema.yml
│   │   └── marts/             # Modelos de marts
│   │       ├── sales_by_product.sql
│   │       ├── sales_by_category.sql
│   │       └── schema.yml
│   ├── dbt_project.yml        # Configuração do projeto DBT
│   └── profiles.yml           # Perfis de conexão DBT
├── trino/                     # Configuração do Trino
│   └── etc/
│       └── catalog/
│           └── iceberg.properties  # Configuração do catálogo Iceberg
├── docker-compose.yaml        # Configuração do Docker Compose
├── Dockerfile                 # Dockerfile para Airflow com DBT
└── requirements.txt           # Dependências Python
```

## Começando

### Pré-requisitos

- Docker e Docker Compose
- Git

### Configuração e Execução

1. Clone este repositório:
   ```
   git clone <repository-url>
   cd airflow-dbt-iceberg
   ```

2. Inicie os serviços:
   ```
   docker-compose up -d
   ```

3. Acesse a interface do Airflow:
   - URL: http://localhost:8080
   - Usuário: airflow
   - Senha: airflow

4. Acesse a interface do Trino:
   - URL: http://localhost:8081
   - Sem autenticação necessária

5. Acesse o Console do MinIO:
   - URL: http://localhost:9001
   - Usuário: minioadmin
   - Senha: minioadmin

### Executando o Exemplo

1. Na interface do Airflow, ative o DAG `dbt_iceberg_example`
2. Dispare o DAG manualmente ou aguarde a execução programada
3. O DAG irá:
   - Inicializar o MinIO com dados de exemplo
   - Criar tabelas Iceberg no Trino
   - Inserir dados nas tabelas Iceberg
   - Executar modelos DBT para transformar os dados
   - Gerar documentação DBT

### Detalhes do DAG (dbt_iceberg_dag.py)

O arquivo `dbt_iceberg_dag.py` define um DAG do Airflow que orquestra todo o processo de ETL. Ele contém dados de exemplo e as seguintes funções principais:

#### Dados de Exemplo no DAG

O DAG inclui estruturas de dados Python que definem os dados de exemplo:

```python
# Dados de produtos
sample_data = [
    {"id": 1, "name": "Product A", "category": "Electronics", "price": 199.99, "date": "2023-01-15"},
    {"id": 2, "name": "Product B", "category": "Clothing", "price": 49.99, "date": "2023-01-16"},
    {"id": 3, "name": "Product C", "category": "Electronics", "price": 299.99, "date": "2023-01-17"},
    {"id": 4, "name": "Product D", "category": "Home", "price": 129.99, "date": "2023-01-18"},
    {"id": 5, "name": "Product E", "category": "Clothing", "price": 79.99, "date": "2023-01-19"},
]

# Dados de vendas
sample_sales = [
    {"sale_id": 101, "product_id": 1, "quantity": 2, "total": 399.98, "date": "2023-01-20"},
    {"sale_id": 102, "product_id": 2, "quantity": 1, "total": 49.99, "date": "2023-01-20"},
    # ... mais registros de vendas
]
```

#### Funções Principais

1. **initialize_minio()**: 
   - Cria um bucket chamado 'iceberg-data' no MinIO se não existir
   - Faz upload de dados de exemplo de produtos e vendas em formato JSON

2. **create_iceberg_tables()**:
   - Cria o schema 'raw' no catálogo Iceberg se não existir
   - Cria tabelas Iceberg para produtos e vendas com formato Parquet
   - Define a localização das tabelas no MinIO

   Estrutura da tabela de produtos:
   ```sql
   CREATE TABLE IF NOT EXISTS iceberg.raw.products (
       id INTEGER,
       name VARCHAR,
       category VARCHAR,
       price DOUBLE,
       date DATE
   )
   ```

   Estrutura da tabela de vendas:
   ```sql
   CREATE TABLE IF NOT EXISTS iceberg.raw.sales (
       sale_id INTEGER,
       product_id INTEGER,
       quantity INTEGER,
       total DOUBLE,
       date DATE
   )
   ```

3. **insert_data_into_trino()**:
   - Limpa dados existentes nas tabelas para evitar duplicações
   - Insere dados de exemplo de produtos e vendas nas tabelas Iceberg

   Operações de inserção:
   ```sql
   -- Limpar dados existentes
   DELETE FROM iceberg.raw.products
   DELETE FROM iceberg.raw.sales

   -- Inserir dados de produtos
   INSERT INTO iceberg.raw.products (id, name, category, price, date)
   VALUES (?, ?, ?, ?, ?)

   -- Inserir dados de vendas
   INSERT INTO iceberg.raw.sales (sale_id, product_id, quantity, total, date)
   VALUES (?, ?, ?, ?, ?)
   ```

O fluxo de execução do DAG segue a seguinte ordem:
```
initialize_minio → create_iceberg_tables → insert_data_into_trino → dbt_debug → dbt_run → dbt_docs_generate
```

Cada tarefa depende da conclusão bem-sucedida da tarefa anterior, garantindo um fluxo de trabalho ordenado e confiável.

## Dados de Exemplo e Transformações

Este projeto inclui dados de exemplo que demonstram um fluxo de trabalho típico de análise de vendas:

1. **Dados Brutos**:
   - **Produtos**: Informações sobre produtos, incluindo ID, nome, categoria, preço e data
     - Exemplo: Produtos em categorias como "Electronics", "Clothing" e "Home"
     - Armazenados inicialmente como JSON no MinIO e depois carregados em tabelas Iceberg
   - **Vendas**: Registros de vendas com ID da venda, ID do produto, quantidade, valor total e data
     - Exemplo: Transações de vendas com diferentes quantidades e valores totais
     - Relacionados aos produtos através do campo product_id

2. **Transformações**:
   - **Modelos de Staging**: Limpam e padronizam os dados brutos
     - `stg_products`: Prepara os dados de produtos para análise
     - `stg_sales`: Prepara os dados de vendas para análise

   - **Modelos de Marts**: Criam visões de negócios agregadas
     - `sales_by_product`: Agrega vendas por produto, calculando quantidade total vendida, receita total e data da última venda
     - `sales_by_category`: Agrega vendas por categoria de produto, calculando quantidade total vendida, receita total e data da última venda

Estas transformações demonstram como o DBT pode ser usado para construir modelos de dados incrementalmente, começando com dados brutos e criando camadas de abstração que facilitam a análise de negócios.

## Explorando os Resultados

Após a execução bem-sucedida do DAG:

1. Consulte os dados transformados no Trino:
   ```sql
   SELECT * FROM iceberg.marts.sales_by_product;
   SELECT * FROM iceberg.marts.sales_by_category;
   ```

2. Explore os arquivos de dados no MinIO:
   - Navegue até o bucket `iceberg-data` no Console do MinIO
   - Explore os dados brutos e os metadados do Iceberg

## Personalizando o Exemplo

### Adicionando Novas Fontes de Dados

1. Adicione dados de exemplo à função `initialize_minio` no DAG
2. Crie novas tabelas na função `create_iceberg_tables`
3. Adicione novos modelos de staging no projeto DBT
4. Crie novos modelos de marts que usam os modelos de staging

### Modificando Transformações

1. Edite os modelos DBT no diretório `dbt_project/models`
2. Atualize os arquivos schema.yml para documentar e testar as alterações
3. Execute o DAG para aplicar as alterações

## Solução de Problemas

- **DAG falha na tarefa initialize_minio**: Verifique se o MinIO está em execução e saudável
- **DAG falha na tarefa create_iceberg_tables**: Verifique os logs do Trino e do Hive Metastore
- **DAG falha nas tarefas DBT**: Verifique os logs das tarefas para erros do DBT

## Recursos Adicionais

- [Documentação do Apache Airflow](https://airflow.apache.org/docs/)
- [Documentação do DBT](https://docs.getdbt.com/)
- [Documentação do Apache Iceberg](https://iceberg.apache.org/docs/latest/)
- [Documentação do Trino](https://trino.io/docs/current/)

## Conclusão

Este projeto demonstra uma arquitetura moderna de processamento de dados que combina várias tecnologias de código aberto para criar um pipeline de dados completo e escalável. A integração do Airflow, DBT e Iceberg oferece uma solução robusta para:

- Orquestração de fluxos de trabalho de dados
- Transformação de dados usando SQL
- Armazenamento eficiente com controle de versão e evolução de esquema
- Consulta de dados de alto desempenho

Esta configuração pode ser usada como ponto de partida para implementar pipelines de dados em ambientes de produção, com as devidas considerações de segurança, escalabilidade e monitoramento.

Para explorar mais a fundo, considere:

1. Adicionar mais fontes de dados e transformações
2. Implementar testes de qualidade de dados com DBT
3. Configurar alertas e monitoramento no Airflow
4. Explorar recursos avançados do Iceberg, como viagem no tempo (time travel) e otimizações de desempenho

O código está estruturado de forma modular, facilitando a extensão e adaptação para casos de uso específicos.
