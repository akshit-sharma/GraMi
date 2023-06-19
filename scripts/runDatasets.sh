#!/bin/bash
# Run the dataset experiments

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'  # Reset color

timeout_human_duration="1m"

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

show_progress() {
  local duration=$1
  local timeout_duration=$2
  local progress_bar_width=$3
  local java_pid=$4

  local interval=10
  local progress=0

  while [ $duration -gt 0 ]; do

    if ! ps -p ${java_pid} > /dev/null; then
      local elapsed_seconds=$((timeout_duration - duration))
      local elapsed_minutes=$((elapsed_seconds / 60))
      local elapsed_hours=$((elapsed_minutes / 60))
      local elapsed_time=$(printf "%02d:%02d:%02d" $elapsed_hours $elapsed_minutes $elapsed_seconds)

      echo -ne "\r${GREEN}command finished${RESET}$(printf ' %.0s' $(seq 1 $progress_bar_width)) [Time Taken: <${elapsed_time}]"
      echo
      return
    fi
    # Calculate the progress percentage
    local percentage=$((100 * (timeout_duration - duration) / timeout_duration))

    # Calculate the remaining time
    local remaining_seconds=$((duration % 60))
    local remaining_minutes=$((remaining_seconds / 60 % 60))
    local remaining_hours=$((remaining_minutes / 3600))
    local remaining_time=$(printf "%02d:%02d:%02d" $remaining_hours $remaining_minutes $remaining_seconds)

    # Calculate the number of filled and empty slots in the progress bar
    local filled_slots=$((progress_bar_width * percentage / 100))
    local empty_slots=$((progress_bar_width - filled_slots))

    # Print the progress bar and remaining time
    echo -ne "\r[${GREEN}$(printf '=%.0s' $(seq 1 $filled_slots))${RESET}$(printf ' %.0s' $(seq 1 $empty_slots))]"
    echo -ne " ${percentage}% Remaining: ${remaining_time}"

    # Wait for the interval
    sleep $interval
    duration=$((duration - interval))
  done
  #                                                                                          : 00:00:00
  echo -ne "\r${YELLOW}command timed out${RESET}$(printf ' %.0s' $(seq 1 $progress_bar_width))          "
  echo
}

convert_to_seconds() {
  local time_string=$1

  local seconds=0

  # Check if the input contains hours
  if [[ $time_string == *h* ]]; then
    local hours_part="${time_string%%h*}"
    seconds=$((seconds + hours_part * 3600))
    time_string="${time_string#*h}"
  fi

  # Check if the input contains minutes
  if [[ $time_string == *m* ]]; then
    local minutes_part="${time_string%%m*}"
    seconds=$((seconds + minutes_part * 60))
    time_string="${time_string#*m}"
  fi

  # Check if the input contains seconds
  if [[ $time_string == *s* ]]; then
    local seconds_part="${time_string%%s*}"
    seconds=$((seconds + seconds_part))
  fi

  echo "$seconds"
  return 0
}

check_timeout() {
  local timeout_human=$1
  local time_pid=$2
  local filepath=$3
  shift 3
  local command="$@"

  java_pid=$(pgrep -P $time_pid java)
  echo -e "${YELLOW}timePid:${RESET} ${time_pid}${YELLOW}, javaPid:${RESET} ${java_pid}"

  timeout_duration=$(convert_to_seconds "$timeout_human")

  show_progress $timeout_duration $timeout_duration 50 $java_pid

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

  check_timeout ${timeout_human_duration} $time_pid $tmpfilepath $command

  filepath="timings/${filename}"
  mv ${tmpfilepath} ${filepath}
}

run_command "test10" 1
run_command "test10" 2
run_command "p2p-Gnutella08" 100
