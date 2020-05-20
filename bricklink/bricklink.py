import requests
from requests_oauthlib import OAuth1

class BricklinkException(Exception):
    def __init__(self, code, message, description):
        self.code = code
        self.message = message
        self.description = description
        super(BricklinkException, self).__init__(self)

    def __str__(self):
        return "%d - %s: %s" % (self.code, self.message, self.description)

class BricklinkRequester(object):
    """ Helper class which performs the actual REST calls to Bricklink """
    BRICKLINK_URL = "https://api.bricklink.com/api/store/v1"

    def _parse_optional_params(self, **optional):
        optional_params = []
        for key, value in optional.items():
            if value:
                optional_params.append("%s=%s" % (key, str(value)))

        return "?%s" % ("&".join(optional_params))

    def _parse_response(self, response):
        if response['meta']['code'] != 200:
            raise BricklinkException(**response['meta'])

        return response['data']

    def __init__(self, oauth_consumer_key, oauth_consumer_secret,
                 oauth_access_token, oauth_access_token_secret):
        """
        Creates object which allows authenticated REST calls to Bricklink
        :param oauth_consumer_key: The Consumer key provided by Bricklink
        :param oauth_consumer_secret: The Consumer secret provided by Bricklink
        :param oauth_access_token: The Access Token provided by Bricklink
        :param oauth_access_token_secret: The Access Token Secret provided by Bricklink
        """
        self._oauth = OAuth1(
            oauth_consumer_key,
            oauth_consumer_secret,
            oauth_access_token,
            oauth_access_token_secret
        )

    def get(self, path, **optional):
        """
        Performs a GET REST call to the Bricklink API
        :param path: The Bricklink API path
        :param optional: All optional parameters that neesd to be passed to Bricklink
        :return: BricklinkException when request failed, otherwise the parsed JSON from the API
        """
        response = requests.get(
            self.BRICKLINK_URL + path + self._parse_optional_params(**optional),
            auth=self._oauth
        ).json()

        return self._parse_response(response)

class BricklinkApi(object):
    """
    Class represents the Bricklink (https://bricklink.com) API
    """
    def __init__(self, requester):
        """
        Creates object which allows commands to the Bricklink API
        :param requester: Helper object that performs the actual REST calls to the Bricklink API
        """
        self._requester = requester

    def getCatalogItem(self, type, no):
        """
        Returns information about the specified item in the Bricklink catalog
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :return: If the call is successful it returns a catalog item with the following data structure:
            {
                'item':  {
                    'no': string,
                    'name': string,
                    'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                    'category_id': integer
                },
                'alternate_no': string,
                'image_url': string,
                thumbnail_url': string,
                'weight': fixed point number (2 decimals),
                'dim_x': string (2 decimals),
                'dim_y': string (2 decimals),
                'dim_z': string (2 decimals),
                'year_released': integer,
                'description': string,
                'is_obsolete': boolean,
                'language_code': string
            }
        """

        if type == "SET":
            if '-' not in str(no):
                no = "%s-1" % no

        print(no)

        return self._requester.get("/items/%s/%s" % (type, no))

    def getCatalogItemImage(self, type, no, color_id):
        """
        Returns the image URL of the specified item by color
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: Bricklink color id
        :return: If the call is successful it returns a catalog item with the following data structure
            {
                'color_id': integer,
                'thumbnail_url': string,
                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                'no': string
            }
        """
        return self._requester.get("/items/%s/%s/images/%d" % (type, no, color_id))

    def getCatalogSupersets(self, type, no, color_id = None):
        """
        Returns a list of items that included the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :return: If the call is successful it returns a list of superset entries with the following data structure:
            [
                {
                    'color_id': integer,
                    'entries': [
                        {
                            'quantity': integer,
                            'appears_as': string (A: Alternate, C: Counterpart, E: Extra, R: Regular),
                            'item'  => {
                                'no': string,
                                'name': string,
                                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                                'category_id': integer
                            }
                        },
                        {
                            etc...
                        }
                    ]
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get(
            "/items/%s/%s/supersets" % (type, no),
            color_id=color_id)

    def getCatalogSubsets(self, type, no, color_id = None, box = None, instruction = None,
                          break_minifigs = None, break_subsets = None):
        """
        Returns a list of items that are included in the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :param box: (Optional) Indicates whether the set includes the original box
        :param instruction: (Optional) Indicates whether the set includes the original instruction
        :param break_minifigs: (Optional) Indicates whether the result breaks down minifigs as parts
        :param break_subsets: (Optional) Indicates whether the result breaks down sub sets as parts
        :return: If the call is successful it returns a list of subset entries with the following data structure:
            [
                {
                    'match_no': integer,
                    'entries': [
                        {
                            'color_id': integer,
                            'quantity': integer,
                            'extra_quantity': integer,
                            'is_alternate': boolean,
                            'is_counterpart': boolean,
                            'item': {
                                'no': string,
                                'name': string,
                                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                                'category_id': integer
                            }
                        },
                        {
                            etc...
                        }
                    ]
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get(
            "/items/%s/%s/subsets" % (type, no),
            box=box,
            break_minifigs=break_minifigs,
            break_subsets=break_subsets,
            color_id=color_id,
            instruction=instruction
        )

    def getCatalogPriceGuide(self, type, no, color_id = None, guide_type = None, new_or_used = None,
                             country_code = None, region = None, currency_code = None, vat = None):
        """
        Returns the price statistics of the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :param guide_type: (Optional) Indicates which statistics should be provided. Acceptable values are:
                            "sold": get the price statistics of "Last 6 months sales"
                            "stock": get the price statistics of "Current items for sale" (default)
        :param new_or_used: (Optional) Indicates the condition of the items that are included in the statistics.
                            Acceptable values are:
                                "N": new item (default), "U": used item
        :param country_code: (Optional) The result includes only items in stores which are located in the specified country
        :param region: (Optional) The result includes only items in stores which are located in the specified region
        :param currency_code: (Optional) The currency in which prices should be returned
        :param vat: (Optional) Indicates that price will include VAT for items from VAT enabled stores.
                    Acceptable values are: "N": exclude VAT (default), "Y": include VAT
        :return: If the call is successful it returns a price guide resource with the following data structure:
            {
                'item': {
                    'no': string,
                    'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX)
                },
                'new_or_used': string (N: New, U: Used)
                'currency_code': string,
                'min_price': fixed point number (4 decimals),
                'max_price': fixed point number (4 decimals),
                'avg_price': fixed point number (4 decimals),
                'qty_avg_price': fixed_point_number (4 decimals),
                'unit_quantity': integer,
                'total_quantity': integer,
                'price_detail': [
                    {
                        'quantity': integer,
                        'unit_price': fixed point number (4 decimals),
                        'shipping_available': string
                            __OR__
                        'quantity': integer,
                        'unit_price': integer,
                        'seller_country_code': string,
                        'buyer_country_code': string,
                        'date_ordered': timestamp
                    },
                    {
                        etc...
                    }
                ]
            }
        """
        return self._requester.get("/items/%s/%s/price" % (type, no),
                                   color_id=color_id,
                                   guide_type=guide_type,
                                   new_or_used=new_or_used,
                                   country_code=country_code,
                                   region=region,
                                   currency_code=currency_code,
                                   vat=vat
                                   )

    def getCatalogKnownColors(self, type, no):
        """
        Returns currently known colors of the item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :return: If the call is successful it returns a list of known colors with the following data structure:
            [
                {
                    'color_id': integer,
                    'quantity': integer
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get("/items/%s/%s/colors" % (type, no))

    def getColorList(self):
        """
        Retrieves a list of colors defined in the Bricklink catalog
        :return: A list of defined colors with the following data structure:
            [
                {
                    'color_id': integer,
                    'color_name': string,
                    'color_code': string,
                    'color_type': string
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get("/colors")

    def getColor(self, color_id):
        """
        Retrieves information about a specific Bricklink color
        :param color_id: The Bricklink color id
        :return: If the call is successful it returns color information in the following data structure:
            {
                'color_id': integer,
                'color_name': string,
                'color_code': string,
                'color_type': string
            }
        """
        return self._requester.get("/colors/%s" % color_id)

    def getCategoryList(self):
        """
        Retrieves a list of all categories defined in the Bricklink catalog
        :return: If the call is successful it returns a list Bricklink catalog categories in the following data structure:
            [
                {
                    'category_id': integer,
                    'category_name': string,
                    'category_parent': integer (0 is root)
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get("/categories")

    def getCategory(self, category_id):
        """
        Retrieves information about a specific Bricklink catalog category
        :param category_id: The bricklink category ID
        :return: If the call is successful it returns information about a category in the following data structure:
            {
                'category_id': integer,
                'category_name': string,
                'category_parent': integer (0 is root)
            }
        """
        return self._requester.get("/categories/%d" % category_id)

    def getElementId(self, type, no):
        """
        Retrieves Part-color-code (A.K.A. element id) of a specificed item
        :param type: The type of item. Acceptable values: PART
        :param no: Identification number of the item
        :return: If the call is successful it returns a list of item mapping resources in the following data structure:
            [
                {
                    'item': {
                        'no': string,
                        'type': string (PART)
                    },
                    'color_id': integer,
                    'color_name': string,
                    'element_id': string
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get("/item_mapping/%s/%s" % (type, no))

    def getItemNumber(self, element_id):
        """
        Retrieves a BL Catalog item number by Part-color-code (A.K.A. element id)
        :param element_id: Element ID of the item in a specified color
        :return: If the call is successful it returns a list of item mapping resources in the following data structure:
            [
                {
                    'item': {
                        'no': string,
                        'type': string (PART)
                    },
                    'color_id': integer,
                    'color_name': string,
                    'element_id': string
                },
                {
                    etc...
                }
            ]
        """
        return self._requester.get("/item_mapping/%s" % element_id)

    def getImageURL(self, type, no, color_id):
        if type == 'PART':
            return 'https://www.bricklink.com/P/' + str(color_id) + '/' + str(no) + '.jpg'
        elif type == 'MINIFIG':
            return 'https://www.bricklink.com/M/' + str(no) + '.jpg'
        else:
            # Standard image placeholder
            return 'https://www.bricklink.com/P/1/3003.jpg'
