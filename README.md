# SOTickets

SOTickets is an API for concert tickets management system.

Once provided with all neccesery keys and tokens located in .env and docker-compose.yml, you should be able to run all of its containers using:

```
$ docker-compose up -d
```

There will be 3 containers:
1. The Redis container - which will handle OTP and seat selections for each concert.
2. The MySQL container - which will have the DB for long-term memory (such as users credentials)
3. The app container - which will handle requests for concerts information and seat selection.

In order to work with this API, you will send requests to via Postman or CURL to:
```
http://0.0.0.0:5000/<API_ROUTE>
````

## Users routes
1.
### Request

`POST /register/`

    curl -i -H "Content-Type: application/json" -d '{"email": "a@a.com", "username": "testuserA", "password": "123456"} 'http://0.0.0.0:5000/bands/

### Response

    Status: 200 OK \ False - 503 (error) \ False - 401 (user already exists)
    Message: if any error occurred, we would like to inform the client 


Bands routes

Concerts routes

