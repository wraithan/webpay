define('cli', ['settings', 'lib/tracking'], function(settings, tracking) {
    'use strict';

    var $progress = $('#progress');
    var $doc = $(document);
    var $body = $('body');
    var bodyData = $body.data();
    var $win = $(window);
    var $fullErrorScreen = $('#full-screen-error');
    var gaTrackingCategory = settings.ga_tracking_category;

    var cli = {
        win: $win,
        doc: $doc,
        body: $body,
        hasTouch: ('ontouchstart' in window) ||
                   window.DocumentTouch &&
                   document instanceof DocumentTouch,
        bodyData: bodyData,
        mozPaymentProvider: window.mozPaymentProvider || {},
        showProgress: function(msg) {
            if ($progress.length) {
                msg = msg || bodyData.loadingMsg;
                $progress.find('.txt').text(msg);
                $progress.show();
            }
        },
        hideProgress: function() {
            if ($progress.length) {
                $progress.hide();
            }
        },
        focusOnPin: function(config) {
            // Ensure the trusted-ui is currently in focus
            // which is necessary to ensure the reliability of
            // the keyboard appearing when we focus the input
            // (bug 863328).
            if (window.focus) {
                window.focus();
            }
            config = config || {};
            var $form = config.$form || $('#pin');
            var $toHide = config.$toHide || null;
            var $toShow = config.$toShow || null;
            var $pinBox = $form.find('.pinbox');
            var $input = $form.find('input[name="pin"]');
            if ($toHide && $toHide.length) {
                $toHide.hide();
            }
            this.hideProgress();
            if ($toShow && $toShow.length) {
                $toShow.show();
                $doc.trigger('check-long-text');
            }
            if ($pinBox.length && !$pinBox.hasClass('error')) {
                console.log('[cli] Focusing pin');
                $input.focus();
            }
        },
        trackWebpayClick: function(e) {
            if (e && e.target) {
                var trackEventData = $(e.target).data('trackEvent');
                if (trackEventData) {
                    this.trackWebpayEvent(trackEventData);
                }
            }
        },
        trackWebpayEvent: function(options) {
            options = options || {};
            tracking.trackEvent(gaTrackingCategory, options.action, options.label, options.value, options.nonInteraction);
        },
        showFullScreenError: function(options) {
            options = options || {};
            options = _.defaults(options,  {
                errorHeading: bodyData.fullErrorHeading,
                errorDetail: bodyData.fullErrorDetail,
                errorButton: bodyData.fullErrorButton
            });

            // Use this to hide content that should be hidden when
            // the full-screen error is displayed.
            $body.addClass('full-error');


            $fullErrorScreen.find('.heading').text(options.errorHeading);
            $fullErrorScreen.find('.detail').text(options.errorDetail);
            $fullErrorScreen.find('.button').text(options.errorButton);
            if (options.secondaryButton) {
                var $btn = $fullErrorScreen.find('.button');
                $btn.addClass('half');
                $secondaryBtn = $btn.clone();
                
            }
            $fullErrorScreen.show();

            // Setup click handler for one time use.
            $fullErrorScreen.find('.button').one('click', function(e){
                e.stopPropagation();
                e.preventDefault();
                $fullErrorScreen.hide();
                $body.removeClass('full-error');
                if (options.callback) {
                    options.callback();
                }
            });

        }
    };

    console.log('[cli] mozPaymentProvider.iccIds?', cli.mozPaymentProvider.iccIds);
    console.log('[cli] mozPaymentProvider.mcc?', cli.mozPaymentProvider.mcc);
    console.log('[cli] mozPaymentProvider.mnc?', cli.mozPaymentProvider.mnc);
    console.log('[cli] mozPaymentProvider.sendSilentSms?', cli.mozPaymentProvider.sendSilentSms);

    return cli;
});
