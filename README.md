# Microservices Assignment

A small microservices-based backend system built using Django, FastAPI, PostgreSQL, NATS, and Docker.

The system demonstrates API Gateway architecture, asynchronous event-driven communication, message acknowledgement, database persistence, and containerized deployment.

---

## Architecture

```text
                    Client
                       |
                       | HTTP
                       v
                +--------------+
                | API Gateway  |
                |    :8003     |
                +------+-------+
                       |
                       | HTTP
                       v
                +--------------+
                | User Service |
                |    :8001     |
                +------+-------+
                       |
                 +-----+-----+
                 |           |
                 | SQL       | Publish Event
                 v           v
           +-----------+   +-----------+
           | PostgreSQL|   |   NATS    |
           |   :5433   |   |   :4222   |
           +-----------+   +-----+-----+
                                 |
                                 | user.created
                                 v
                       +--------------------+
                       | Notification       |
                       | Service :8002      |
                       +--------------------+
