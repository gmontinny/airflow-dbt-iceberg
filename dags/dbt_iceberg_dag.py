from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import boto3
import json
import os
import trino

# Argumentos padrão para o DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Definir o DAG
dag = DAG(
    'dbt_iceberg_example',
    default_args=default_args,
    description='Um exemplo de DAG que executa modelos DBT em tabelas Iceberg',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['dbt', 'iceberg', 'example'],
)

# Função para inicializar o bucket MinIO e fazer upload de dados de exemplo
def initialize_minio():
    """Criar bucket MinIO e fazer upload de arquivos de dados de exemplo se não existirem"""
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1',
        verify=False,
    )

    # Criar bucket se não existir
    try:
        s3_client.head_bucket(Bucket='iceberg-data')
        print("Bucket 'iceberg-data' já existe")
    except:
        s3_client.create_bucket(Bucket='iceberg-data')
        print("Bucket 'iceberg-data' criado")

    # Criar dados de exemplo
    sample_data = [
        {"id": 1, "name": "Product A", "category": "Electronics", "price": 199.99, "date": "2023-01-15"},
        {"id": 2, "name": "Product B", "category": "Clothing", "price": 49.99, "date": "2023-01-16"},
        {"id": 3, "name": "Product C", "category": "Electronics", "price": 299.99, "date": "2023-01-17"},
        {"id": 4, "name": "Product D", "category": "Home", "price": 129.99, "date": "2023-01-18"},
        {"id": 5, "name": "Product E", "category": "Clothing", "price": 79.99, "date": "2023-01-19"},
    ]

    # Fazer upload dos dados de exemplo
    s3_client.put_object(
        Bucket='iceberg-data',
        Key='raw/products/products.json',
        Body=json.dumps(sample_data),
        ContentType='application/json'
    )
    print("Dados de produtos de exemplo carregados")

    # Criar dados de vendas de exemplo
    sample_sales = [
        {"sale_id": 101, "product_id": 1, "quantity": 2, "total": 399.98, "date": "2023-01-20"},
        {"sale_id": 102, "product_id": 2, "quantity": 1, "total": 49.99, "date": "2023-01-20"},
        {"sale_id": 103, "product_id": 3, "quantity": 1, "total": 299.99, "date": "2023-01-21"},
        {"sale_id": 104, "product_id": 1, "quantity": 1, "total": 199.99, "date": "2023-01-21"},
        {"sale_id": 105, "product_id": 4, "quantity": 3, "total": 389.97, "date": "2023-01-22"},
        {"sale_id": 106, "product_id": 5, "quantity": 2, "total": 159.98, "date": "2023-01-22"},
        {"sale_id": 107, "product_id": 2, "quantity": 4, "total": 199.96, "date": "2023-01-23"},
    ]

    # Fazer upload dos dados de vendas de exemplo
    s3_client.put_object(
        Bucket='iceberg-data',
        Key='raw/sales/sales.json',
        Body=json.dumps(sample_sales),
        ContentType='application/json'
    )
    print("Dados de vendas de exemplo carregados")

# Função para criar tabelas Iceberg no Trino
def create_iceberg_tables():
    """Criar tabelas Iceberg no Trino se não existirem"""
    # Usar o cliente Python do Trino para executar SQL
    conn = trino.dbapi.connect(
        host='trino',
        port=8080,
        user='airflow',
        catalog='iceberg',
        schema='default',
    )

    cursor = conn.cursor()

    # Criar schema
    cursor.execute("CREATE SCHEMA IF NOT EXISTS iceberg.raw")

    # Criar tabela de produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iceberg.raw.products (
        id INTEGER,
        name VARCHAR,
        category VARCHAR,
        price DOUBLE,
        date DATE
    )
    WITH (
        format = 'PARQUET',
        location = 's3a://iceberg-data/raw/products/tables/'
    )
    """)

    # Criar tabela de vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iceberg.raw.sales (
        sale_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total DOUBLE,
        date DATE
    )
    WITH (
        format = 'PARQUET',
        location = 's3a://iceberg-data/raw/sales/tables/'
    )
    """)

    cursor.close()
    conn.close()

    print("Tabelas Iceberg criadas com sucesso")

# Tarefa para inicializar o MinIO com dados de exemplo
init_minio_task = PythonOperator(
    task_id='initialize_minio',
    python_callable=initialize_minio,
    dag=dag,
)

# Tarefa para criar tabelas Iceberg
create_tables_task = PythonOperator(
    task_id='create_iceberg_tables',
    python_callable=create_iceberg_tables,
    dag=dag,
)

# Tarefa para executar o debug do DBT para verificar conexões
dbt_debug_task = BashOperator(
    task_id='dbt_debug',
    bash_command='cd /opt/airflow/dbt_project && dbt debug --profiles-dir .',
    dag=dag,
)

# Tarefa para executar os modelos DBT
dbt_run_task = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir .',
    dag=dag,
)

# Tarefa para gerar documentação do DBT
dbt_docs_task = BashOperator(
    task_id='dbt_docs_generate',
    bash_command='cd /opt/airflow/dbt_project && dbt docs generate --profiles-dir .',
    dag=dag,
)

# Definir dependências entre tarefas
init_minio_task >> create_tables_task >> dbt_debug_task >> dbt_run_task >> dbt_docs_task
