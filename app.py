import tempfile
import shutil
import subprocess

from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import constants


MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
</head>
<body>
  <form name="form" action="/upload" method="POST" enctype="multipart/form-data">
    <span>Crash dump file: </span><input type="file" name="file"/>
  <input type="submit" value="Upload" name="submit">
</form>
</body>
</html>
"""
CRASHDUMP_EXTENSION = '.dmp'
CRASHDUMP_HEADER = 'MDMP'


app = Flask(__name__)
# Limit uploads to 1M
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


@app.route('/', methods=['GET'])
def main():
  return MAIN_TEMPLATE


@app.route('/upload', methods=['POST'])
def upload():
  if not 'file' in request.files or not request.files['file'].filename:
    return 'Missing crash dump.', 400

  file = request.files['file']
  if not file.filename.endswith(CRASHDUMP_EXTENSION):
    return 'Must upload a crash dump .dmp file.', 400

  with tempfile.NamedTemporaryFile() as f:
    shutil.copyfileobj(file.stream, f)
    f.flush()
    f.seek(0)
    try:
      if f.read(len(CRASHDUMP_HEADER)).decode('ascii') != CRASHDUMP_HEADER:
        return 'Invalid dump file.', 400
    except:
      return 'Invalid dump file.', 400
    try:
      out = subprocess.check_output([constants.MINIDUMP_STACKWALK, f.name, constants.SYMBOL_PATH])
      return '<pre>%s</pre>' % out.decode('utf-8')
    except subprocess.CalledProcessError as e:
      return e.output, 400

  return 'ok'
