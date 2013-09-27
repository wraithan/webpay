require(['cli', 'id', 'pay/bango'], function(cli, id, bango) {
    "use strict";
    var bodyData = cli.bodyData,
        on_success;

    function watchForceAuth(_onSuccess) {
        id.watch({
            onlogin: function _resetLogin(assertion) {
                console.log('[reset] nav.id onlogin');
                $.post(bodyData.verifyUrl, {assertion: assertion})
                    .done(function _resetLoginSuccess(data) {
                        console.log('[reset] login success, reverified: %s', data.was_reverified);
                        if (data.was_reverified) {
                            bango.prepareAll(data.user_hash).done(function _forceAuthReady() {
                                cli.trackWebpayEvent({'action': 'reset force auth',
                                                      'label': 'Login Success'});
                                _onSuccess.apply(this);
                            });
                        } else {
                            cli.showFullScreenError();
                        }
                    })
                    .fail(function _resetLoginError(data) {
                        console.log('[reset] login error: %s', JSON.stringify(data));
                        cli.trackWebpayEvent({'action': 'reset force auth',
                                              'label': 'Login Failure'});
                    });
            },
            onlogout: function _resetLogout() {
                console.log('[reset] nav.id onlogout');
                cli.trackWebpayEvent({'action': 'reset force auth',
                                      'label': 'Logged Out'});
            }
        });
    }

    function startForceAuth() {
        id.request({
            experimental_forceAuthentication: true,
            oncancel: function() {
                cli.trackWebpayEvent({'action': 'reset force auth',
                                      'label': 'Cancelled'});
                window.location.href = bodyData.cancelUrl;
            }
        });
    }

    $('.force-auth-button').on('click', function(evt) {
        evt.preventDefault();
        cli.showProgress(bodyData.personaMsg);
        if (window.localStorage.getItem('reset-step') === 'pin') {
            /* You've already re-signed in. */
            console.log('[reset] requesting focus on pin (already re-signed in)');
            cli.focusOnPin({ $toHide: $('#confirm-pin-reset'), $toShow: $('#enter-pin') });
            window.localStorage.removeItem('reset-step');
            return;
        }
        if (bodyData.forceAuthResult !== 'show-pin') {
            on_success = function _resetBounceSuccess() {
                /* We are going to bounce you to the reset-step after login,
                 * but you've already entered your login, so we'll store that.
                 */
                console.log('[reset] logged in, bouncing to', bodyData.resetUrl);
                window.localStorage.setItem('reset-step', 'pin');
                window.location.href = bodyData.resetUrl;
            };
        } else {
            on_success = function _resetLoginSuccess() {
                /* You are in the reset step and you've logged in,
                 * let's show you a pin.
                 */
                console.log('[reset] requesting focus on pin (logged-in)');
                cli.focusOnPin({ $toHide: $('#confirm-pin-reset'), $toShow: $('#enter-pin') });
            };
        }
        watchForceAuth(on_success);
        startForceAuth();
    });
});
