#!/bin/bash
#

set -e

py=env/bin/python3

mvn compile

mkdir -p ./artifacts/dumps

bash ./scripts/runDatasets.sh

cp ./timings/* ./artifacts/dumps/

$py ./python/processIndividuals.py
$py ./python/TanStackv8Table.py
