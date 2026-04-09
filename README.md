Описание задачи в TZ.pdf

## Запуск:

``git clone https://github.com/xor26/Fintech_tz.git``

```cd Fintech_tz```

```docker compose build```

```docker compose up```

Замечание:

Используются стандартные порты для ребита, постгреса и фастапи
5672, 15672, 5432, 8000

При старте надо убедиться что они свободны

## Работа:
Примеры запросов и ответов

#### Makepayment
```
curl --location 'http://0.0.0.0:8000/api/v1/payments' \
--header 'Idempotency-Key: 12' \
--header 'X-API-Key: TRUST_ME_BRO_IM_AUTHORIZED' \
--header 'Content-Type: application/json' \
--data '{
    "amount": 123,
    "currency": "USD",
    "description": "for stuff",
    "meta_data": {},
    "webhook_url": "http://0.0.0.0:7000/"
}'
```
Ответ:
```
{
    "amount": 123,
    "currency": "USD",
    "description": "for stuff",
    "meta_data": {},
    "webhook_url": "http://0.0.0.0:7000/"
}
```


#### Get payments
Запрос
```
curl --location 'http://0.0.0.0:8000/api/v1/payments' \
--header 'X-API-Key: TRUST_ME_BRO_IM_AUTHORIZED'
```
Ответ
```
[
    {
        "uid": "27b88b72-7ecb-4d04-b376-ea3c263e8aa1",
        "amount": "123.00",
        "currency": "USD",
        "description": "for stuff",
        "meta_data": {},
        "status": "succeeded",
        "webhook_url": "http://0.0.0.0:7000/",
        "created_at": "2026-04-09T01:14:05.152308",
        "processed_at": "2026-04-09T01:14:11.202298"
    }
]
```

Пример для конкретного идишника
Запрос
```
curl --location 'http://0.0.0.0:8000/api/v1/payments/27b88b72-7ecb-4d04-b376-ea3c263e8aa1' \
--header 'X-API-Key: TRUST_ME_BRO_IM_AUTHORIZED'
```
Ответ
```
{
    "uid": "27b88b72-7ecb-4d04-b376-ea3c263e8aa1",
    "amount": "123.00",
    "currency": "USD",
    "description": "for stuff",
    "meta_data": {},
    "status": "succeeded",
    "webhook_url": "http://0.0.0.0:7000/",
    "created_at": "2026-04-09T01:14:05.152308",
    "processed_at": "2026-04-09T01:14:11.202298"
}
```

#### Эти же запросы в Postman
https://web.postman.co/workspace/My-Workspace~1ed9a1dd-db9d-4492-8e01-a7c5c9f83294/collection/7692863-3f5473f3-1b3f-4c1b-a063-1f3edd8f2ff3?action=share&source=copy-link&creator=7692863