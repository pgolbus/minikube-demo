import click
import requests
import json
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

BASE_URL = f"http://{os.getenv('FLASK_APP_HOST')}:{os.getenv('FLASK_APP_PORT')}"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option('-g', '--get', 'key', help='Get the value of the specified Redis key.')
@click.option('-s', '--set', 'json_path', type=click.Path(exists=True), help='Set the Redis key/value pair using the specified JSON file.')
def main(key, json_path):
    """
    CLI tool to interact with the Flask app's Redis endpoints.

    Options:
        -g, --get: Get the value of the specified Redis key.
        -s, --set: Set the Redis key/value pair using the specified JSON file.
    """
    if key:
        # Perform GET request
        logger.info(f'Attempting to get value for key: {key}')
        try:
            response = requests.get(f'{BASE_URL}/get/{key}')
            response.raise_for_status()
            click.echo(response.json())
            logger.info(f'Successfully retrieved value for key: {key}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Error getting value for key: {key}, Error: {e}')
            click.echo(f'Error: {e}')
    elif json_path:
        # Perform POST request
        logger.info(f'Attempting to set key/value pair from file: {json_path}')
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
            response = requests.post(
                f'{BASE_URL}/set',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )
            response.raise_for_status()
            click.echo(response.json())
            logger.info(f'Successfully set key/value pair from file: {json_path}')
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(f'Error setting key/value pair from file: {json_path}, Error: {e}')
            click.echo(f'Error: {e}')
    else:
        click.echo('Please provide either --get <key> or --set <path to json>')

if __name__ == '__main__':
    main()