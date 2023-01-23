from aiohttp import web
import json
import os
import random
import logging

"""
Simple Python REST API providing Weather Data from given JSON File
"""

async def handle_weather(request):
    """ returns a random weather """
    rnd = random.choice(weather_data)
    return web.json_response(data=rnd)


def load_weather(path: str):
    """ loads weather data from path """
    with open(path) as f:
        data = f.read()
        return json.loads(data)

async def handle_health(request):
    """ returns health_status """
    logging.debug(f"Trying to health_check")
    body = {
        'status':'OK',
        'comment':'Weather_API is healthy.'
    }
    return web.json_response(body, status=200)

app = web.Application()
app.add_routes([
    web.get('/weather', handle_weather),
    web.get('/health', handle_health)])

weather_data = load_weather("./rdu-weather-history.json")

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(levelname)8s  %(message)s',
    )

    port = os.environ.get("HTTP_PORT")
    logging.info(f"Starting server on port {port}")
    web.run_app(app, port=int(port))
