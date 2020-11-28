#-*-coding:utf-8
from flask import Flask,render_template, request,send_from_directory
from flask_cors import CORS
import time
app = Flask(__name__)
CORS(app, resources=r'/*')
UPLOAD_FOLDER = 'photo'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOW_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOW_EXTENSIONS

from PIL import Image
import numpy as np
import os
import io
from flask import make_response
@app.route('/mockup_vertext/mockup_generate_vertext', methods=['POST'])
def mockup_generate_vertext():
    os.chdir("/root/code/mockup_vertext")
    files = request.files
    output_dir = "output_mocuk" + ranstr(15)
    if os.path.exists(output_dir):
	os.system("rm " + output_dir + " -rf")
    os.mkdir(output_dir)
    for key in files.keys():
        img = Image.open(io.BytesIO(files[key].stream.read()))
        generate_vertex(img, output_dir, files[key].filename)
    os.system("zip -r " + output_dir + ".zip " + output_dir)

    return send_from_directory('./', filename=output_dir + ".zip", as_attachment=True)

#-------------------------------------------------------------------------------------------------------
import mockup_check_process
@app.route('/mockup_vertext/mockup_check', methods=['POST'])
def mockup_check():
    files = request.files
    for key in files.keys():
        img = Image.open(io.BytesIO(files[key].stream.read()))
        res = mockup_check_process.process(img)
        return str(res['message'])
    
#-------------------------------------------------------------------------------------------------------
import parse_psd_package
@app.route('/mockup_vertext/parse_psd_package_process', methods=['POST'])
def parse_psd_package_process():
    files = request.files
    for key in files.keys():
        files[key].save(os.path.join("data",files[key].filename))
        output_dir = os.path.join("data",files[key].filename.split("_")[0])
        parse_psd_package.process_mockup_package(files[key].filename,"data")
    return send_from_directory('./', filename=output_dir + ".zip", as_attachment=True)
#-------------------------------------------------------------------------------------------------------

@app.route("/mockup_vertext/download_test",methods=['POST'])
def download_test():
    return send_from_directory("./",filename="run.py",as_attachment=True)

def index2rgb(i):
    r = int(i / (256 * 256))
    g = int(i % (256 * 256) / 256)
    b = int(i % 256)
    return (r, g, b, 255)


def generate_vertex(im, output_dir, filename):
    print(filename)
    im_data = np.asarray(im)[:, :, 3]
    im_new = Image.new("RGBA", (2048, 2048), (255, 255, 255, 0))
    index = 0
    xy_res = im_data.nonzero()
    xmin = np.min(xy_res[1])
    xmax = np.max(xy_res[1])
    ymin = np.min(xy_res[0])
    ymax = np.max(xy_res[0])
    x_hold = max(int((xmax-xmin) / 15),20)
    y_hold = max(int((ymax-ymin) / 15),20)
    alpha = 1.5
    print(xmin, xmax, ymin, ymax)
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if xmin - alpha * x_hold <= x and x <= xmax + alpha * x_hold and ymin - alpha * y_hold <= y and y <= ymax + alpha * y_hold:
                if x % x_hold == 0 and y % y_hold == 0:
                    # print x,y
                    for i in range(13):
                        for j in range(13):
                            im_new.putpixel((int(x + i), int(y + j)), index2rgb(index))
            index += 1

    im_new.save(os.path.join(output_dir, filename))


import random
def ranstr(num):
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt




    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

# import werkzeug
# werkzeug.datastructures.FileStorage
