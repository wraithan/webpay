# This script should be called from within Jenkins

cd $WORKSPACE
VENV=$WORKSPACE/venv
SETTINGS=mkt

echo "Starting build on executor $EXECUTOR_NUMBER..." `date`
echo "Setup..." `date`

# Make sure there's no old pyc files around.
find . -name '*.pyc' | xargs rm

if [ ! -d "$VENV/bin" ]; then
  echo "No virtualenv found.  Making one..."
  virtualenv $VENV --system-site-packages
fi

source $VENV/bin/activate

pip install -U --exists-action=w --no-deps -q -r requirements/test.txt

cat > webpay/settings/local.py <<SETTINGS
from webpay.settings.base import *
LOG_LEVEL = logging.ERROR
DATABASES = {
    'default': {
        'ENGINE': 'mysql_pool',
        'NAME': 'zamboni_mkt',
        'TEST_NAME': 'test_zamboni_webpay',
        'USER': 'hudson',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset' : 'utf8',
            'use_unicode' : True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
}
CACHE_BACKEND = 'caching.backends.locmem://'
CELERY_ALWAYS_EAGER = True
STATIC_URL = ''
SECRET_KEY = 'cheese will make you live forever'

SETTINGS

echo "Starting tests..." `date`
export FORCE_DB='yes sir'

python manage.py test -v 2 --noinput --logging-clear-handlers --with-xunit
rv=$?

echo 'shazam!'
exit $rv
