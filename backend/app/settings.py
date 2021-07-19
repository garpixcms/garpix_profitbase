from garpixcms.settings import *  # noqa

INSTALLED_APPS += [  # noqa
    'garpix_profitbase',
]

PAGE_MIXIN = 'garpix_page.models.BasePage'
EMPTY_MIXIN = 'garpix_profitbase.models.empty_mixin.EmptyMixin'
