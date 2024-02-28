# Multithreaded API webserver

PLEASE DON'T USE SAFARI, THEIR REQUEST SUCK

## Run server

Change coordinator host and coordinator port to match at

```
dbHost = hostname
dbPort = portNum
```

```
python3 server.py serverPort
```

## Accepted API path

### GET /api/tweet - get a list of all tweets

#### Request
```
GET /api/tweet
Cookies : usr=username
```

#### Response
```
200

{
    'key' : 'username:content'
}
```

### POST /api/tweet - create a new tweets on the server

#### Request
```
POST /api/tweet
Content-Type : application/x-www-form-urlencoded

content='tweet'
```

#### Response

Success
```
200
```

Not login
```
401
```

Server/Database Error
```
500
```

### PUT /api/tweet/[tweet-id] - Update tweet tweet-id to a new value.

#### Request
```
PUT /api/tweet/[tweet-id]
Content-Type : application/x-www-form-urlencoded

content='tweet'
```

#### Response

Success
```
200
```

Not login
```
401
```

Server/Database Error
```
500
```

### POST /api/login - Log into tweet

#### Request
```
POST /api/login
Content-Type : application/x-www-form-urlencoded

usr='Username'
```

#### Response

Success
```
200
Set-Cookies : usr='Username'
```

Server Error
```
500
```

# Distributed Database

## Run

### Worker

```bash
python3 worker.py [port]
```

### Coordinator
```bash
python3 coordinator [worker1Host:worker1Port] [worker2Host:worker2Port]
```

## Request

### Get all tweet
```
{
    'type' : 'GET'
}
```

### Set/Creat tweet
```
{
    'type' : 'SET'
    'key' : 'str'
    'value' : 'contentStr'
}
```

## Response

### Response to SET request
```
{
    'type' : 'SET-RESPONSE',
    'status' : 500,
    'message' : 'DB error, cannot change tweet, plese try again later'
}
```

```
{
    'type' : 'SET-RESPONSE',
    'status' : 409,
    'message' : 'The tweet cannot be updated right now please try again'
}
```

```
{
    'type' : 'SET-RESPONSE',
    'status' : 200,
    'message' : 'The tweet sucessfully update'
}
```

```
{
    'type' : 'SET-RESPONSE',
    'status' : 200,
    'message' : 'The tweet is set sucessfully'
}
```

### Response to GET request
```
{
    'type' : 'GET-RESPONSE',
    'status' : 500,
    'message' : 'Cannot get the tweet'
}
```

```
{
    'type' : 'GET-RESPONSE',
    'value' : {
    'type' : 'DB',
    'db' : database
    },
    'status' : 200,
    'message' : 'The tweet is get sucessfully'
}
```

# Acknowledgement

The project idea and description was taken from an assignment from my beloved Distributed Computing Instructor Robert Guderian
