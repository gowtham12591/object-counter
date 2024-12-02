#!/bin/bash

# Get cores per socket (physical cores per processor)
cores_per_socket=$(sysctl -n hw.physicalcpu)

# macOS systems typically have only one socket, so num_sockets = 1
num_sockets=1

# Calculate total number of physical cores
num_physical_cores=$((cores_per_socket * num_sockets))

# Pull the TensorFlow Serving development image with ARM support
docker pull emacski/tensorflow-serving:latest

# Run TensorFlow Serving
docker run \
    --name=tfserving \
    -p 8500:8500 \
    -p 8501:8501 \
    -v "$(pwd)/tmp/model:/models" \
    -e OMP_NUM_THREADS=$(sysctl -n hw.physicalcpu) \
    -e TENSORFLOW_INTER_OP_PARALLELISM=2 \
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$(sysctl -n hw.physicalcpu) \
    emacski/tensorflow-serving:latest \
    --model_config_file=/models/model_config.config