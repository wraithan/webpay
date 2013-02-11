import functools
import hashlib

from django.conf import settings

from cef import log_cef as _log_cef

from lib.solitude.api import client


def get_uuid(email):
    """
    Given an email returns the hash of the email for this site. This will be
    consistent for each email for this site and can be used as the uuid in
    solitude. Because the leakage of the email is more of a privacy concern
    than a security concern, we are just doing a simple sha1 hash.

    :email: the email to hash.
    """
    if not isinstance(email, basestring):
        raise ValueError('get_uuid requires a string or unicode')
    hashed = hashlib.sha1()
    hashed.update(email)
    return '%s:%s' % (settings.DOMAIN, hashed.hexdigest())


def get_user(request):
    try:
        return request.session.get('uuid')
    except KeyError:
        raise KeyError('Attempt to access user without it being set, '
                       'did you use the user_verified decorator?')


def set_user(request, email):
    request.session['email'] = email
    uuid = get_uuid(email)
    request.session['uuid'] = uuid
    buyer = client.get_buyer(uuid)
    set_user_has_pin(request, buyer.get('pin', False))
    set_user_has_confirmed_pin(request, buyer.get('pin_confirmed', False))
    set_user_reset_pin(request, buyer.get('needs_pin_reset', False))
    set_user_has_new_pin(request, buyer.get('new_pin', False))


def set_user_has_pin(request, has_pin):
    request.session['uuid_has_pin'] = has_pin


def set_user_has_confirmed_pin(request, has_confirmed_pin):
    request.session['uuid_has_confirmed_pin'] = has_confirmed_pin


def set_user_reset_pin(request, reset_pin):
    request.session['uuid_needs_pin_reset'] = reset_pin


def set_user_has_new_pin(request, has_new_pin):
    request.session['uuid_has_new_pin'] = has_new_pin


def log_cef(msg, request, **kw):
    g = functools.partial(getattr, settings)
    severity = kw.get('severity', g('CEF_DEFAULT_SEVERITY', 5))
    cef_kw = {
        'msg': msg,
        'signature': request.get_full_path(),
        'config': {
            'cef.product': 'WebPay',
            'cef.vendor': g('CEF_VENDOR', 'Mozilla'),
            'cef.version': g('CEF_VERSION', '0'),
            'cef.device_version': g('CEF_DEVICE_VERSION', '0'),
            'cef.file': g('CEF_FILE', 'syslog'),
        },
    }
    _log_cef(msg, severity, request.META.copy(), **cef_kw)
