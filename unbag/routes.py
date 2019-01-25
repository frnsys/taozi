import config
from flask import Blueprint, send_from_directory

bp = Blueprint('main', __name__)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)

@bp.route('/<slug>')
def built_file(slug):
    return send_from_directory(config.BUILD_FOLDER, slug)
