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