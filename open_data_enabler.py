from flask import Flask, jsonify, request
from waitress import serve
import os, inspect, logging
from dcat_offering_mapper import read_rdf_to_dict, extract_params, create_offering

PROGRAM_NAME = inspect.stack()[0][1].split('.py', 1)[0].split('\\')[-1].split('/')[-1]
PROGRAM_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_LEVEL = 10
LOG_MAX_FILE_SIZE_BYTES = 1024 * 1024 * 10
LOG_MAX_NUMBER_FILES = 2

# Set up logger
logger = logging.getLogger(PROGRAM_NAME + "_logger")
if not os.path.exists(PROGRAM_PATH + '/logs/'):
    os.makedirs(PROGRAM_PATH + '/logs/')

from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(PROGRAM_PATH + '/logs/' + PROGRAM_NAME + '.log',
                              maxBytes=LOG_MAX_FILE_SIZE_BYTES,
                              backupCount=LOG_MAX_NUMBER_FILES)
formatter = logging.Formatter('{asctime} {levelname:<8s} | {filename}:{lineno:<4} [{funcName:^30s}] | {message}', style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

app = Flask(__name__)

@app.route('/newoffering', methods=['POST'])
def new_offering():
    req = request.get_json()
    if 'url' not in req:
        return jsonify({'error': 'URL not provided'}), 400
    url = req['url']
    logger.info(f"Crawling URL: {url}")
    try:
        rdf_dict = read_rdf_to_dict(url)
        params_dict = extract_params(rdf_dict)
        offering = create_offering(params_dict)
        return jsonify(offering), 200
    
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logger.info("Serving on port 4020")
    serve(app, host='0.0.0.0', port=4020)
