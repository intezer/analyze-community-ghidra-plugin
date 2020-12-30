# Plugin for Intezer Analyze in Ghidra (python 2.7 - jython)
# @author
# @category Examples.Python
# @keybinding
# @menupath
# @toolbar

import sys
import os

if (os.name == "Posix") and (("Linux") in os.uname()):
    sys.path.append('/usr/lib/python2.7/dist-packages')
    sys.path.append('/usr/local/lib/python2.7/dist-packages')
elif ("Darwin") in os.uname():
    sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
    sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/lib/site-python')
    sys.path.append('/Library/Python/2.7/site-packages')
    sys.path.append(os.path.expanduser('~')+'/Library/Python/2.7/lib/python/site-packages')
elif os.name == "nt" or os.environ.get('os') == "Windows_NT":
    sys.path.append('C:\\Python27\\lib\\site-packages')
else:
    print('Whelp, something went wrong.')

import hashlib
import traceback
import requests
import time
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.dom import minidom

VERSION = '0.1'
INTEZER_API_KEY = os.environ.get('INTEZER_API_KEY')
BASE_URL = os.environ.get('INTEZER_BASE_URL', 'https://analyze.intezer.com')
API_URL = '{}/api'.format(BASE_URL)
DIR = os.path.dirname(os.path.abspath("__file__"))
PATH_TO_XML = os.path.join(DIR, "items.xml")

URLS = {
    'get_access_token': '{}/v2-0/get-access-token'.format(API_URL),
    'create_ghidra_plugin_report': '{}/v1-2/files/{{}}/community-ida-plugin-report'.format(API_URL)
}

MESSAGES = {
    'missing_api_key': 'Please set INTEZER_API_KEY in your environment variables',
    'file_not_open': 'Please open a file to analyze',
    'file_not_exists': 'Problem occurred while opening file',
    'file_not_searched': 'Please analyze the file first on Intezer Analyze. The sha256 is: {}',
    'not_supported_file': 'File type not supported for creating Intezer Analyze Ghidra report',
    'authentication_failure': 'Failed to authenticate Intezer service',
    'connection_error': 'Failed to connect to the Intezer cloud platform',
    'no_genes': 'No genes where extracted from the file',
}


class PluginException(Exception):
    pass


class Proxy:
    def __init__(self, api_key):
        self._api_key = api_key
        self._session = None

    @property
    def session(self):
        if not self._session:
            session = requests.session()
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
            session.headers = {'User-Agent': 'ghidra_plugin/{}'.format(VERSION)}
            self._session = session
        return self._session

    def init_access_token(self):
        if 'Authorization' not in self.session.headers:
            response = requests.post(URLS['get_access_token'], json={'api_key': self._api_key})
            response.raise_for_status()

            token = 'Bearer {}'.format(response.json()['result'])
            self.session.headers['Authorization'] = token

    def _post(self, url_path, **kwargs):
        self.init_access_token()
        retries = 5
        retries_counter = 0
        while retries_counter <= retries:
            response = self.session.post(url_path, **kwargs)
            if 299 >= response.status_code >= 200:
                return response
            else:
                time.sleep(2)
                retries_counter += 1
        return None

    def _get(self, url_path, **kwargs):
        self.init_access_token()
        return self.session.get(url_path, **kwargs)

    def create_plugin_report(self, sha256, functions_data):
        response = self._post(URLS['create_ghidra_plugin_report'].format(sha256), json={'functions_data': functions_data})
        if response.status_code == 404:
            raise PluginException(MESSAGES['file_not_searched'].format(sha256))

        if response.status_code == 409:
            raise PluginException(MESSAGES['not_supported_file'])

        if response.status_code != 201:
            raise Exception(response.reason)

        result_url = response.json()['result_url']

        return result_url

    def get_plugin_report(self, result_url):
        retries = 5
        retries_counter = 0
        while retries_counter <= retries:
            response = self._get(API_URL + result_url)
            if response.status_code == 202:
                time.sleep(2)
                retries_counter += 1
            else:
                response.raise_for_status()
                return response.json()['result']


class CodeIntelligenceHelper:
    def __init__(self):
        self._proxy = Proxy(INTEZER_API_KEY)
        self._imagebase = None
        self._entrypoint = None

    @property
    def entrypoint(self):
        if not self._entrypoint:
            self._entrypoint = None
        return self._entrypoint

    @property
    def imagebase(self):
        if not self._imagebase:
            self._imagebase = (currentProgram.getImageBase().offset)
        return self._imagebase

    def _get_function_map(self, sha256):

        functions_data = []
        function_manager = currentProgram.getFunctionManager()
        functions = function_manager.getFunctions(1)
        image_base = int("0x{}".format(str(currentProgram.imageBase)), 16)

        for f in functions:
            function_start_address = f.getEntryPoint()
            function_end_address = f.getBody().getMaxAddress()

            start_address_as_int = int("0x{}".format(str(function_start_address)), 16)
            end_address_as_int = int("0x{}".format(str(function_end_address)), 16)

            functions_data.append({'start_address': long(start_address_as_int - image_base),
                                   'end_address': long(end_address_as_int - image_base + 1)})

        result_url = self._proxy.create_plugin_report(sha256, functions_data)
        ghidra_plugin_report = self._proxy.get_plugin_report(result_url)

        if not ghidra_plugin_report['functions']:
            raise PluginException(MESSAGES['no_genes'])

        functions_map = {}
        for function_address, record in ghidra_plugin_report['functions'].iteritems():
            absolute_address = self._get_absolute_address(int(function_address))
            functions_map[absolute_address] = {'function_address': absolute_address}
            functions_map[absolute_address].update(record)
        return functions_map

    def _get_absolute_address(self, function_address):
        return hex(self.imagebase + function_address)

    def _enrich_function_map(self, function_map): 

        fm = currentProgram.getFunctionManager()
        for function_absolute_address in function_map:
            n = ""  # needed for the cast from string to Address

            n = function_absolute_address.replace('L', '')
            address = currentProgram.getAddressFactory().getAddress(n)
            function_name = fm.getFunctionContaining(address)

            try:
                function_start_address = function_name.getEntryPoint()

                function_map[function_absolute_address]['function_address'] = "0x{}".format(str(function_start_address))
                function_map[function_absolute_address]['function_name'] = str(function_name)
            except AttributeError as ex:
                function_map[function_absolute_address]['function_address'] = function_absolute_address
                function_map[function_absolute_address]['function_name'] = ""  # Failed resolve function name

        return function_map

    def write_xml_file(self, functions_map):

        def prettify(elem):
            """Return a pretty-printed XML string for the Element.
            """
            rough_string = ElementTree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")

        root = Element('Data')

        for key in functions_map.keys():
            entry = SubElement(root, 'gene')
            function_address = SubElement(entry, "function_address")
            function_name = SubElement(entry, "function_name")
            software_type = SubElement(entry, "software_type")
            code_reuse = SubElement(entry, "code_reuse")

            try:
                function_address.text = functions_map[key]["function_address"]
            except KeyError as ex:
                print("Error in key = {0} when getting function_address. meta = ({1})".format(key, functions_map[key]))

            try:
                function_name.text = functions_map[key]["function_name"]
            except KeyError as ex:
                print("Error in key = {0} when getting function_name. meta = ({1})".format(key, functions_map[key]))

            software_type.text = ','.join(map(str, functions_map[key]["software_type"]))
            for e in functions_map[key]["code_reuse"]:
                code_reuse.text = e

        print(">>>Done building xml. Writing xml...")

        output_file = open(PATH_TO_XML, 'w')
        output_file.write(prettify(root))
        output_file.close()

    def create_function_map(self, sha256):
        function_map = self._get_function_map(sha256)
        function_map = self._enrich_function_map(function_map)
        self.write_xml_file(function_map)


class IntezerAnalyzePlugin():

    def run(self):
        if not INTEZER_API_KEY:
            print(MESSAGES['missing_api_key'])
            return

        path = currentProgram.getExecutablePath()
        program_name = currentProgram.getName()
        creation_date = currentProgram.getCreationDate()
        language_id = currentProgram.getLanguageID()
        compiler_spec_id = currentProgram.getCompilerSpec().getCompilerSpecID()

        if not path:
            print(MESSAGES['file_not_exists'])
            return

        print(">>> Program Info:\n" \
              ">>>\t%s:\n" \
              "\t%s_%s\n" \
              "\t(%s)\n" \
              "\t%s" % (
                  program_name, language_id, compiler_spec_id, creation_date, path))

        try:
            with open(path, 'rb') as fh:
                sha256 = hashlib.sha256(fh.read()).hexdigest()
        except Exception:
            print(MESSAGES['file_not_exists'])
            return

        print(">>> file SHA : " + sha256)
        print('>>> Start analyzing file...')

        try:
            helper = CodeIntelligenceHelper()

            helper.create_function_map(sha256)
            print(">>> Calling java script")
            runScript("XMLParser.java")

            print('>>> Done analyzing, loading data')
        except Exception:
            traceback.print_exc()


runner = IntezerAnalyzePlugin()
runner.run()
