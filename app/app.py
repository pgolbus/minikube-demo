from flask import Flask, request, jsonify
import redis
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Redis connection using environment variables
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)

@app.route('/healthcheck', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check requested')
    return jsonify({'status': 'healthy'}), 200

@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    """
    Retrieve the value for the given Redis key.

    Args:
        key (str): The key to look up in Redis.

    Returns:
        JSON response with the key-value pair or an error message if the key is not found.
    """
    app.logger.info(f'Request to get value for key: {key}')
    try:
        value = redis_client.get(key)
        if value is None:
            app.logger.warning(f'Key not found: {key}')
            return jsonify({'error': 'Key not found'}), 404
        app.logger.info(f'Key found: {key}, Value: {value.decode("utf-8")}')
        return jsonify({key: value.decode('utf-8')}), 200
    except Exception as e:
        app.logger.error(f'Error retrieving key: {key}, Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/set', methods=['POST'])
def set_value():
    """
    Set a Redis key-value pair from the provided JSON payload.

    Returns:
        JSON response indicating success or an error message.
    """
    app.logger.info('Request to set key-value pair')
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        if not key or not value:
            app.logger.warning('Key and value are required')
            return jsonify({'error': 'Key and value are required'}), 400
        redis_client.set(key, value)
        app.logger.info(f'Successfully set key: {key} with value: {value}')
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        app.logger.error(f'Error setting key-value pair, Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_APP_HOST'),
        port=int(os.getenv('FLASK_APP_PORT')),
        debug=True
    )