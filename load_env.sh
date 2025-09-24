#!/bin/bash

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE file not found in current directory"
    exit 1
fi

echo "Loading environment variables from: $ENV_FILE"

while IFS='=' read -r key value || [ -n "$key" ]; do
    if [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    export "$key=$value"
    echo "Exported: $key"
done < "$ENV_FILE"
