FROM openjdk:8-jre-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    wget \
    netcat \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV HADOOP_VERSION=3.3.4
ENV HIVE_VERSION=3.1.3
ENV HADOOP_HOME=/opt/hadoop
ENV HIVE_HOME=/opt/hive
ENV PATH=$HADOOP_HOME/bin:$HIVE_HOME/bin:$PATH

# Download and install Hadoop
RUN mkdir -p $HADOOP_HOME && \
    wget -q https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt && \
    mv /opt/hadoop-${HADOOP_VERSION}/* $HADOOP_HOME && \
    rm hadoop-${HADOOP_VERSION}.tar.gz && \
    rm -rf /opt/hadoop-${HADOOP_VERSION}

# Download and install Hive
RUN mkdir -p $HIVE_HOME && \
    wget -q https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz && \
    tar -xzf apache-hive-${HIVE_VERSION}-bin.tar.gz -C /opt && \
    mv /opt/apache-hive-${HIVE_VERSION}-bin/* $HIVE_HOME && \
    rm apache-hive-${HIVE_VERSION}-bin.tar.gz && \
    rm -rf /opt/apache-hive-${HIVE_VERSION}-bin

# Add AWS S3 JARs for S3 support
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_VERSION}/hadoop-aws-${HADOOP_VERSION}.jar -P $HADOOP_HOME/share/hadoop/common/lib/ && \
    wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -P $HADOOP_HOME/share/hadoop/common/lib/

# Create directories for Hive metastore
RUN mkdir -p /opt/hive/conf /opt/hive/data/warehouse /opt/hive/data/metastore

# Copy configuration files
COPY conf/hive-site.xml $HIVE_HOME/conf/
COPY conf/core-site.xml $HADOOP_HOME/etc/hadoop/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Starting Hive Metastore"\n\
$HIVE_HOME/bin/schematool -dbType derby -initSchema\n\
$HIVE_HOME/bin/hive --service metastore\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 9083

ENTRYPOINT ["/entrypoint.sh"]