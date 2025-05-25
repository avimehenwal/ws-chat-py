# ws-chat-py

## Setup - start project

1. clone the repository
2. Create a python virtual environemnt
3. Install requirements
4. Run docker-compose to start backend service
5. Run backend


```sh
python3 -m venv .venv
source .venv/bin/activate

docker compose up -d
```

## Tech stack used

### Dependencies

| S.No | dependency                    | purpose                  |
| ---- | ----------------------------- | ------------------------ |
| 1.   | libretranslate/libretranslate | translations             |
| 2.   | redis                         | analytics and data-store |

## Code Organization

### Modules

1. Health check
2. Jokes API
3. Chat WS API
4. Analytics API