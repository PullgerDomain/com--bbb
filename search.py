import importlib

from django.conf import settings

from pullgerFootPrint.org.bbb import pFP_search
from pullgerInternalControl import pIC_pD
from pullgerInternalControl.pullgerDomain.logging import logger

from pullgerAccountManager import authorizationsServers
from pullgerSquirrel import connectors

from pullgerDevelopmentFramework import dynamic_code

RELOAD_SET = (pFP_search, )


class SearchDomain:
    __slots__ = (
        '_authorized',
        '_connected',
        '_session',
        '_squirrel',
        '_initialized',
        '_squirrel_initialized',
        '_RootLoaded',
        '_library_reloading',
    )

    def __init__(self, session, library_reloading: bool = False, **kwargs):
        self._authorized = False
        self._connected = False
        self._squirrel = None
        self._initialized = False
        self._squirrel_initialized = False
        self._RootLoaded = None
        self._session = session
        self._library_reloading = library_reloading

    @staticmethod
    def required_authorization_servers_options():
        authorization_list = [
            str(None),
        ]

        response = {}
        for cur_auth in authorization_list:
            response[str(cur_auth)] = cur_auth

        return response

    @staticmethod
    def required_connector_options():
        connectors_list = [
            connectors.connector.selenium.chrome.standard,
        ]

        response = {}
        for cur_connector in connectors_list:
            response[str(cur_connector)] = cur_connector

        return response

    @property
    def authorized(self):
        return self._authorized

    @property
    def connected(self):
        return self._connected

    @property
    def squirrel(self):
        return self._squirrel

    @property
    def initialized(self):
        return self._initialized

    @property
    def squirrel_initialized(self):
        return self._squirrel_initialized

    @property
    def RootLoaded(self):
        return self._RootLoaded

    def get(self, id_iso_country, id_iso_state, id_name_city, id_name_category, *args, **kwargs):
        # url = "https://www.linkedin.com/search/results/" + search_scope + "/?origin=FACETED_SEARCH"
        url_domain = "https://www-bbb-org.translate.goog"
        url_postfix = "?_x_tr_sl=ru&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp"
        url_body = f"/{id_iso_country}/{id_iso_state}/{id_name_city}/category/{id_name_category}"
        url = url_domain + url_body + url_postfix

        self._session.get_page(
            url=url,
            page_control_element="//div[@class='stack stack-space-20']",
            delay_before_get=0,
            delay_after_get=0
        )

    def push_next(self):
        number_of_page = pFP_search.get_number_of_page_pagination(session=self._session)
        current_page_number = pFP_search.get_page_number_on_pagination(session=self._session)
        if current_page_number < number_of_page:
            url_next = pFP_search.get_next_url(session=self._session)

            try:
                self._session.get_page(
                    url=url_next,
                    page_control_element="//div[@class='stack stack-space-20']",
                    delay_before_get=0,
                    delay_after_get=0
                )
            except BaseException as e:
                logger.error(
                    msg=f"Error on loading page: {url_next}: description {str(e)}"
                )

            new_page_number = pFP_search.get_page_number_on_pagination(session=self._session)
            if new_page_number == current_page_number:
                logger.warning(
                    msg="Incorrect next operation on pagination"
                )
                return False
            else:
                return True
        else:
            return False

        pIC_pD.Processing(
            msg="Error on code",
            level=50
        )

    def pull(self, *args, **kwargs):
        dynamic_code.lib_reloader(RELOAD_SET)

        list_profiles = []

        is_not_last = True
        # number_of_page = pFP_search.get_number_of_page_pagination(session=self._session)
        while is_not_last is True:
            list_profiles_blocks = pFP_search.get_search_result_list(session=self._session)
            for cur_profile_block in list_profiles_blocks:
                id_name_profile = pFP_search.pull_profile_id(cur_profile_block)
                keys_city = pFP_search.pull_profile_city_keys(cur_profile_block)
                list_profiles.append(
                    {
                        "id_name_profile": id_name_profile,
                        **keys_city
                    }
                )

            number_of_page = pFP_search.get_number_of_page_pagination(session=self._session)
            current_page_number = pFP_search.get_page_number_on_pagination(session=self._session)

            is_not_last = self.push_next()

        response = {
            "meta": {
                "page_loaded": number_of_page,
                "page_count": current_page_number
            },
            "elements": list_profiles
        }

        return response
