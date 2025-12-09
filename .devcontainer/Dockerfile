# GitHub Codespace Spark Development Environment
# Based on Microsoft's Python devcontainer with Spark additions

FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Set Spark and Java versions
ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3
ARG JAVA_VERSION=11

# Install Java (required for Spark)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-${JAVA_VERSION}-jdk \
    wget \
    curl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Download and install Apache Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /opt \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

# Set Spark environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Configure Spark for local development
ENV SPARK_LOCAL_IP=127.0.0.1
ENV SPARK_MASTER_HOST=127.0.0.1

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create workspace directory
WORKDIR /workspaces

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog
