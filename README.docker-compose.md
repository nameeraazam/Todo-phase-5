# Quick Start Guide - Local Development

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+
- Dapr CLI (optional, for advanced features)

## Start All Services

```bash
# From project root
docker-compose up -d
```

## Verify Services

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                  STATUS          PORTS
# todo-kafka            Up              0.0.0.0:9092->9092/tcp
# todo-zookeeper        Up              0.0.0.0:2181->2181/tcp
# todo-dapr-placement   Up              0.0.0.0:50005->50005/tcp
# todo-postgres         Up              0.0.0.0:5432->5432/tcp
# todo-redis            Up              0.0.0.0:6379->6379/tcp
```

## Access Admin UIs

| Service | URL | Credentials |
|---------|-----|-------------|
| Kafka UI | http://localhost:8090 | No auth |
| PgAdmin | http://localhost:8091 | admin@todo.local / admin |
| Dapr Dashboard | http://localhost:8080 | No auth |

## Run Backend with Dapr

```bash
cd backend

# Option 1: With Dapr sidecar (for event-driven features)
dapr run `
  --app-id todo-backend `
  --app-port 8000 `
  --dapr-http-port 3500 `
  --dapr-grpc-port 50001 `
  --components-path ./dapr/components `
  -- uvicorn src.api.main:app --reload --port 8000

# Option 2: Without Dapr (basic features only)
uvicorn src.api.main:app --reload --port 8000
```

## Test Kafka Connection

```bash
# Create a test topic via Kafka UI
# Navigate to http://localhost:8090
# Click on your cluster → Topics → Create Topic
# Topic name: tasks.events

# Or via command line
docker exec -it todo-kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic tasks.events
```

## Test PostgreSQL Connection

```bash
# Connect via psql
docker exec -it todo-postgres psql -U postgres -d todo_db

# Or via PgAdmin
# Navigate to http://localhost:8091
# Server: todo-postgres
# Username: postgres
# Password: postgres
```

## Stop All Services

```bash
# Stop containers (preserves data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Troubleshooting

### Kafka won't start
```bash
# Check logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

### Dapr can't connect to Kafka
```bash
# Verify Kafka is accessible
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check Dapr component config
cat backend/dapr/components/kafka-pubsub.yaml
```

### PostgreSQL connection refused
```bash
# Check if Postgres is healthy
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

## Resource Usage

| Service | Memory | CPU |
|---------|--------|-----|
| Kafka | ~500MB | ~10% |
| Zookeeper | ~100MB | ~5% |
| Dapr Placement | ~50MB | ~2% |
| PostgreSQL | ~200MB | ~5% |
| Redis | ~20MB | ~1% |
| **Total** | **~870MB** | **~23%** |

## Next Steps

1. ✅ Services running
2. ✅ Backend configured
3. → Run database migrations
4. → Start implementing features
