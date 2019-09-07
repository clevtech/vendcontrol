# vendcontrol
Erlan`s project

## Protocol

1. Send money in: `vid:amount`
2. Send open door: `vid:o`
3. Send open inner door: `vid:i`

## Stored data

### Transaction

```
{
    "bid": 23,
    "vid": 12412313,
    "amount": 200,
    "time": object(datetime)
}
```

### Building

```
{
    "bid": 1270369823,
    "name": {
        "ru": "Аэропорт",
        "kz": "Ауежай",
        "qz": "Auezhai",
        "eng": "Airport"
    },
    "number_of_places": 4
}
```

### Vending

```
{
    "vid": 1298746847,
    "bid": 23,
    "amount_all": 120000000,
    "last_time": {
        "amount_from_last": 500000,
        "last_time_open": object(datetime),
        "last_time_open_inner: object(datetime), 
        "times_from_last_time": 5
    },
    "average": {
        "all": 24124,
        "day": 123213,
        "week": 213123,
        "month": 3213321
    }
}
```