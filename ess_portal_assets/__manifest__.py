# -*- coding: utf-8 -*-
{
    'name': "ESS Portal Assets",
    'summary': """
        Employee Web Portal Assets""",
    'description': """
        Employee Self Service Web Portal Assets
    """,
    'author': "Sulman Shaukat &amp; Farooq Arif",
    'company': 'AARSOL & NUST (Joint Venture)',
    'website': "https://www.aarsol.com",
    'category': 'OdooCMS',
    'version': '15.0.0.1',
    'sequence': '1',
    'application': 'false',
    'depends': ['website'],
    # 'depends': ['website','odoocms','cms_notifications','cms_surveys'],
    'data': [
        'views/assets/assets.xml'
    ],
    'assets': {
        'ess_portal_assets.ess_assets': [
            'ess_portal_assets/static/images/favicon.ico',
            'ess_portal_assets/static/src/css/vendors_css.css',
            'ess_portal_assets/static/src/css/style.css',
            'ess_portal_assets/static/src/css/skin_color.css',

            'ess_portal_assets/static/src/js/vendors.min.js',
            'ess_portal_assets/static/src/js/pages/chat-popup.js',
            'ess_portal_assets/static/assets/icons/feather-icons/feather.min.js',
            'ess_portal_assets/static/src/js/template.js',
            'ess_portal_assets/static/src/js/pages/timeline.js',
            'ess_portal_assets/static/assets/vendor_components/jquery-toast-plugin-master/src/jquery.toast.js',
            'ess_portal_assets/static/src/custom_alerts.js',

        ],

    },
}
