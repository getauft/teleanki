import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import logging

TOKEN = 'yMrisgbV4BEAAAAAAAEgMbEuUohPiO1yLTCFVIE-2T58TGlZcIEAydQxBlq92dZc'
#LOCALFILE = 'teleanki.db'
#BACKUPPATH = '/teleanki.db'
dbx = dropbox.Dropbox(TOKEN)
dbx.users_get_current_account()
logging.basicConfig(format='<p>%(asctime)s — %(levelname)s: %(message)s</p>',
                    level=logging.INFO,
                    filename='log.html',
                    filemode='w')
logger = logging.getLogger(__name__)


def upload(LOCALFILE, BACKUPPATH):
    with open(LOCALFILE, 'rb') as f:
        dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
        logger.info('Upload project data base to dropbox server.')


def download(LOCALFILE, BACKUPPATH):
    with open(LOCALFILE, 'wb') as f:
        dbx.files_download_to_file(LOCALFILE, BACKUPPATH)
        logger.info('Download project data base from dropbox server.')


def files_list():
    response = dbx.files_list_folder("/sounds")
    return response.entries