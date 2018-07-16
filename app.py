from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, make_response,g, send_file

import itertools
import os
import shutil

temp_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
if not os.path.exists(temp_location):
    os.makedirs(temp_location)

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = temp_location


def _success(result):
    return '<div class="alert alert-success"><strong>Successfully Scrapped</strong><br>{}</div>'.format('{}'.format(result))


def _fail(reason):
    return '<div class="alert alert-danger"><strong>FAILED</strong><br>{}</div>'.format('Failed - {}'.format(reason))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/download', methods=['POST'])
def download_data():
    try:
        out_path = os.path.join(temp_location, 'github.xlsx')
        import github_scrapper

        github_scrapper.init(request.form.get('commit_url'), request.form.get('cntrb_url'), request.form.get('issues_url'), out_path)
        github_scrapper.parseBasicData()
        github_scrapper.parseCommitData()
        github_scrapper.parseIssuesData()
        github_scrapper.parseContribData()
        github_scrapper.writeTocsv()

        string_t0_return = _success('Please click on Download button to download excel file')

    except Exception as e:
        string_t0_return = _fail(str(e))
    return jsonify({'result': string_t0_return}), 200


@app.route('/return-files', methods=['POST', 'GET'])
def return_files():
    outfile= os.path.join(temp_location, 'github.xlsx')
    try:
        return send_file(outfile, attachment_filename='github.xlsx', as_attachment=True)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True, port=5002)

