#!/bin/bash
# Run the dataset experiments

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'  # Reset color

mkdir -p timings/
temp_dir=$(mktemp -d -t timing.XXXX)

ctrl_c() {
  echo -e "${RED}Script interrupted by user.${RESET}"
  # Terminal all background processes
  kill -- -$$ # Terminal child processes of the script
  exit 1
}

trap ctrl_c SIGINT

send_signal() (
  local pid=$1

  if [ -n "$pid" ] && [ -d "/proc/$pid" ]; then
    echo -e "${RED}Sending SIGINT to ${RESET} $pid"
    if kill -SIGINT "$pid"; then
      return 1
    fi
    return 1
  fi

  return 0
)

check_timeout() {
  local timeout_duration=$1
  local time_pid=$2
  local filepath=$3
  shift 3
  local command="$@"

  java_pid=$(pgrep -P $time_pid java)
  echo -e "${YELLOW}timePid:${RESET} ${time_pid}${YELLOW}, javaPid:${RESET} ${java_pid}"

  sleep "$timeout_duration"

  process_terminated=0
  if [ -n "$java_pid" ] && [ -d "/proc/$java_pid" ]; then
    echo -e "${RED}Process ${java_pid} timed out.${RESET}"
    kill -SIGINT "$java_pid"
    echo "Time: dnf" >> ${filepath}
    process_terminated=1
  fi

  if [ "$process_terminated" -eq 0 ]; then
    echo -e "${GREEN}rerunning command${RESET} with verbose=true."
    ${command} verbose=true >> ${filepath}
  fi
}

run_command() {
  local datagraph=$1
  local support=$2
  local alpha=1.0
  local beta=0

  local filename=${datagraph}-${support}-${alpha}-grami-0.time
  local tmpfilepath=${temp_dir}/${filename}

  echo "freq ${support}" > ${tmpfilepath}
  echo "approxA ${alpha}" >> ${tmpfilepath}
  echo "approxB ${beta}" >> ${tmpfilepath}

  command="java -cp ./GRAMI_DIRECTED_SUBGRAPHS/bin/ Dijkstra.main freq=$support filename=$datagraph.lg datasetFolder=./Datasets/ maxLabelsAppearance=-1 approximate=$alpha approxConst=${beta}"

  echo -e "${GREEN}Running command:${RESET} ${command}"
  (/usr/bin/time -v ${command} 2>&1) >> ${tmpfilepath} &
  time_pid=$!

  check_timeout "60" $time_pid $tmpfilepath $command

  filepath="timings/${filename}"
  mv ${tmpfilepath} ${filepath}
}

run_command "test10" 1
run_command "p2p-Gnutella08" 100
run_command "test10" 2
