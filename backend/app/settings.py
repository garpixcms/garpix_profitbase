from garpixcms.settings import *  # noqa

INSTALLED_APPS += [  # noqa
    'garpix_profitbase',
]

GARPIX_PROFITBASE_CITY_MIXIN = 'garpix_profitbase.models.empty_mixin.EmptyMixin'
GARPIX_PROFITBASE_HOUSE_MIXIN = 'garpix_page.models.BasePage'
GARPIX_PROFITBASE_HOUSE_FLOOR_MIXIN = 'garpix_profitbase.models.empty_mixin.EmptyMixin'
GARPIX_PROFITBASE_HOUSE_SECTION_MIXIN = 'garpix_profitbase.models.empty_mixin.EmptyMixin'
GARPIX_PROFITBASE_PROJECT_MIXIN = 'garpix_page.models.BasePage'
GARPIX_PROFITBASE_PROPERTY_MIXIN = 'garpix_page.models.BasePage'
GARPIX_PROFITBASE_SPECIAL_OFFER_MIXIN = 'garpix_profitbase.models.empty_mixin.EmptyMixin'
