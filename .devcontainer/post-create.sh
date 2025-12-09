#!/bin/bash
# Post-creation setup script for Spark development environment

set -e

echo "=========================================="
echo "Setting up Spark Development Environment"
echo "=========================================="

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install the local functions module in editable mode (if setup.py exists)
if [ -f "setup.py" ]; then
    echo "Installing local package..."
    pip install -e .
fi

# Verify Spark installation
echo "Verifying Spark installation..."
echo "SPARK_HOME: $SPARK_HOME"
echo "JAVA_HOME: $JAVA_HOME"

# Test PySpark
echo "Testing PySpark..."
python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName('test') \
    .master('local[*]') \
    .config('spark.driver.memory', '2g') \
    .getOrCreate()
print('Spark version:', spark.version)
print('PySpark is working correctly!')
spark.stop()
"

# Install Jupyter kernel for PySpark
echo "Setting up Jupyter kernel..."
python3 -m ipykernel install --user --name=pyspark --display-name="PySpark"

# Create a local Spark configuration for development
echo "Creating local Spark configuration..."
mkdir -p ~/.spark-conf
cat > ~/.spark-conf/spark-defaults.conf << EOF
spark.master                     local[*]
spark.driver.memory              2g
spark.executor.memory            2g
spark.sql.shuffle.partitions     10
spark.ui.showConsoleProgress     true
spark.sql.session.timeZone       UTC
EOF

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  - Run 'pyspark' to start an interactive PySpark shell"
echo "  - Run 'spark-submit script.py' to submit a Spark job"
echo "  - Use Jupyter notebooks with the 'PySpark' kernel"
echo "  - Spark UI available at http://localhost:4040 when running jobs"
echo ""
