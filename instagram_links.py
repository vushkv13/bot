# instagram_links.py

import re
import requests
from bs4 import BeautifulSoup
import service

class InstagramLinksCorrect:
    patterns = service.OldPatterns()
    account_link_pattern = re.compile(patterns.account_link_pattern)
    image_link_pattern = re.compile(patterns.image_link_pattern)

    def isAccountLink(self, link):
        return bool(re.match(self.account_link_pattern, link))

    def isImageLink(self, link):
        return bool(re.match(self.image_link_pattern, link))

    def ImageLinkIsValid(self, link):
        if self.isImageLink(link):
            resp = requests.get(link)
            return resp.status_code != 404
        return False

    def AccountLinkIsValid(self, link):
        if self.isAccountLink(link):
            resp = requests.get(link)
            return resp.status_code != 404
        return False

class ParseHashes:
    patterns = service.OldPatterns()
    code_with_hash_pattern = re.compile(r'"code"[ ]*:[ ]*"{}"'.format(patterns.image_hash_pattern))
    hash_pattern = re.compile(patterns.image_hash_pattern)

    def get_hashes(self, page_source):
        temp_result = re.findall(self.code_with_hash_pattern, page_source)
        hashes = []
        for code_with_hash in temp_result:
            temp = re.findall(self.hash_pattern, code_with_hash)
            code, hash = temp[0], temp[1]
            hashes.append(hash)
        return tuple(hashes)

def get_source_by_link(link):
    links_tester = InstagramLinksCorrect()
    if not links_tester.ImageLinkIsValid(link):
        return None
    page_source = requests.get(link).text
    soup = BeautifulSoup(page_source, 'html.parser')
    for meta_tag in soup.find_all('meta'):
        if meta_tag.get('property', None) == 'og:image':
            return meta_tag.get("content", None)

def get_tuple_of_sources_by_account(link):
    links_tester = InstagramLinksCorrect()
    if not links_tester.AccountLinkIsValid(link):
        return None

    page_source = requests.get(link).text
    parser = ParseHashes()
    hashes = parser.get_hashes(page_source)

    sources = []
    for hash in hashes:
        source = get_source_by_link('http://instagram.com/p/{}'.format(hash))
        sources.append(source)
    return tuple(sources)

def get_links_from_message(message):
    patterns = service.NewPatterns()
    acc_reg = re.compile(patterns.account_link_pattern)
    im_reg = re.compile(patterns.image_link_pattern)
    account_links = re.findall(acc_reg, message)
    image_links = re.findall(im_reg, message)
    return account_links, image_links