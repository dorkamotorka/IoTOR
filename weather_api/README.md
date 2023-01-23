## weather-api

This is an api for weather data

## Usage:

    port:    '4000'  
    route:   '/weather'

example from your machine or weather_api's container
 
    'curl -f localhost:4000/weather'

example from somewhere in dockers network:

    'curl -f weather_api:4000/weather'

expected output: 

    {"date": "2018-03-17", "tmin": 34, "tmax": 71, "prcp": 0.27, "snow": 0.0, "snwd": 0.0, "awnd": 6.26}

## Healthchecking:

Weather-API performs a simple health-based test on the `/health` API endpoint **every 5 seconds** to announce they are healthy, up and working.  
This information is used by **Docker Swarm** to decide if the container should be restarted.

In legacy mode this triggers an event in docker engine (that can be listened for) and changes the status of the container, but no restarting takes place.

## Troubleshooting:

Log of stdout: 

    'sudo docker logs <CONTAINER-ID>'

## Notes:

JSON-file is quite big.
