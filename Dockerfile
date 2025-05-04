FROM apache/airflow:2.9.1-python3.10

USER root
# Instalar pacotes básicos necessários para construção de bibliotecas e compilações
RUN apt-get update && apt-get install -y \
   git \
   build-essential \
   libssl-dev \
   libffi-dev \
   python3-dev \
   curl \
   openjdk-11-jre-headless

# Copiar os requirements
COPY requirements.txt /requirements.txt

# Download and install Trino CLI
RUN curl -L -o /usr/local/lib/trino.jar https://repo1.maven.org/maven2/io/trino/trino-cli/414/trino-cli-414-executable.jar && \
    # Create a wrapper script to execute the JAR file with Java
    echo '#!/bin/bash' > /usr/local/bin/trino && \
    echo 'exec java -jar /usr/local/lib/trino.jar "$@"' >> /usr/local/bin/trino && \
    chmod +x /usr/local/bin/trino && \
    # Verify the file exists and is executable
    ls -la /usr/local/bin/trino && \
    # Make sure it's available in common paths
    cp /usr/local/bin/trino /usr/bin/trino && \
    chmod +x /usr/bin/trino

# Alternar para o usuário airflow para instalar pacotes
USER airflow
RUN pip install --upgrade pip setuptools wheel && \
   pip install -r /requirements.txt && \
   chmod +x /home/airflow/.local/bin/dbt

# Ajustar permissões adicionais necessárias
USER root
# Ensure /usr/local/bin is in PATH for all users
RUN echo "export PATH=\$PATH:/home/airflow/.local/bin:/usr/local/bin" >> /home/airflow/.bashrc && \
    echo "export PATH=\$PATH:/home/airflow/.local/bin:/usr/local/bin" >> /home/airflow/.profile && \
    echo "export PATH=\$PATH:/home/airflow/.local/bin:/usr/local/bin" >> /etc/profile && \
    echo "export PATH=\$PATH:/home/airflow/.local/bin:/usr/local/bin" >> /etc/environment
RUN mkdir -p /opt/airflow/dbt_project && chown -R airflow:root /opt/airflow/dbt_project


USER airflow
