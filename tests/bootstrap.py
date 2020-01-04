import logging
import sys
import six

if six.PY2:
    from unittest2 import TestCase
else:
    from unittest import TestCase

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout)

logger = logging.getLogger(__name__)


class BaseTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
