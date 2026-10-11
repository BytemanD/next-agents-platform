
from nap.db.models import Attachment
from nap.services.storage import STORE_SERVICE


attachment = Attachment(
    creator='guest',
    name='demo.txt'
)
attachment.create()
STORE_SERVICE.save_text(attachment, '你好，hello')
