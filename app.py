import os
import json
import uuid
import threading
import logging
from timeit import default_timer as timer
from flask import Flask, request
import darknet

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/uploads/'

APP = Flask(__name__)
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hold the darknet data
THREAD_DATA = threading.local()

@APP.route("/")
def hello():
  """
  We're just showing a smiley on / so that it's easy to check if the server is
  running.
  """
  return ":)"

@APP.route("/detect", methods=['POST'])
def detect():
  """
  Send an HTTP multipart/form-data post, with an input named "file" set to the
  image you're uploading. A JSON object with any detections will be returned.
  """

  if 'file' not in request.files:
    return json.dumps({
      'status': 'error',
      'message': 'no file found in request body'
    })


  uploaded_file = request.files['file']
  filename = str(uuid.uuid4())
  filepath = os.path.join(APP.config['UPLOAD_FOLDER'], filename)

  # Save the file to the upload folder
  uploaded_file.save(filepath)

  detection_time = timer()
  detections = darknet.detect(THREAD_DATA.net, THREAD_DATA.meta, filepath)
  detection_time = timer() - detection_time

  # Delete the file we saved
  os.remove(filepath)

  # Get our time in milliseconds
  detection_time = int(round((detection_time) * 1000))

  APP.logger.debug('detection: %sms', detection_time)

  matches = []

  for match in detections:
    name, confidence, bounds = match
    center_x, center_y, bounds_w, bounds_h = bounds

    matches.append({
      'name': name,
      'confidence': confidence,
      'center': {
        'x': center_x,
        'y': center_y
      },
      'bounds': {
        'w': bounds_w,
        'h': bounds_h
      }
    })

  return json.dumps({
    'status': 'ok',
    'matches': matches,
    'perf': detection_time
  })

def initialize():
  """
  Load configuration and data into Darknet.

  TODO: Add multi GPU support:
  Darknet can be set to use different GPUs using the flag -gpus 0,1,2, etc
  https://groups.google.com/forum/#!topic/darknet/NbJqonJBTSY
  """
  net, meta = darknet.initialize(
    "./darknet/cfg/yolo.cfg",
    "./blob/yolo.weights",
    "./darknet/cfg/coco.data"
  )

  THREAD_DATA.net = net
  THREAD_DATA.meta = meta

initialize()

if __name__ == "__main__":
  # Run the application if we are running directly
  APP.run(host="0.0.0.0")
else:
  # We are not running directly, configure logging
  GUNICORN_LOGGER = logging.getLogger('gunicorn.error')
  APP.logger.handlers = GUNICORN_LOGGER.handlers
  APP.logger.setLevel(GUNICORN_LOGGER.level)
