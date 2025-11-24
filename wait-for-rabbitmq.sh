#!/bin/bash
# wait-for-rabbitmq.sh

set -e

host="$1"
shift
cmd="$@"

until python3 -c "import socket; socket.create_connection(('$host', 5672), timeout=1)" 2>/dev/null; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done

>&2 echo "RabbitMQ is up - executing command"
exec $cmd
