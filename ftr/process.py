# -*- coding: utf-8 -*-
""" The :func:`~ftr.process.ftr_process` function makes use of all FTR
objects to offer an easy-to-use *one-liner* to integrate in your python
code.

:func:`~ftr.process.ftr_process` is suitable for live extraction (content
currently available on the internet), but also for postponed or post-mortem
extraction where the content was removed from the internet but you still
have the HTML and the original URL handy.

.. note:: as of current version the :func:`~ftr.process.ftr_process`
    wrapper is the only way to get multiple-page articles parsed as a
    whole (eg. all pages extracted, cleaned and appended as one). See
    :class:`~ftr.extractor.ContentExtractor` for details.

.. Copyright 2015 Olivier Cortès <oc@1flow.io>.

    This file is part of the python-ftr project.

    python-ftr is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    python-ftr is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public
    License along with python-ftr. If not, see http://www.gnu.org/licenses/
"""

import logging

import requests

from urllib.parse import urlparse

from .config import ftr_get_config, SiteConfig
from .extractor import ContentExtractor

LOGGER = logging.getLogger(__name__)


def requests_get(url):
    """ Run :func:`requests.get`.

    The cache wrapper uses the default timeout (environment variable
    ``PYTHON_FTR_CACHE_TIMEOUT``, 3 days by default).

    It is used in :func:`ftr_process`.
    """

    LOGGER.info('Fetching %s…', url)
    return requests.get(url)


def sanitize_next_page_link(next_page_link, base_url):
    """ Convert relative links or query_string only links to absolute URLs. """

    if not next_page_link.startswith('http'):
        if next_page_link.startswith('?'):
            # We have some "?current_page=2" scheme.
            next_page_link = base_url + next_page_link

        if next_page_link.startswith('/'):
            # We have a server-relative path.

            u = urlparse(base_url)
            proto, host_and_port = u.scheme, u.netloc

# except:
# LOGGER.error('Could not split “%s” to get schema/host parts, '
# 'next_page_link “%s” will be unusable.',
# base_url, next_page_link)

# TODO only do if succ
            next_page_link = '{0}://{1}{2}'.format(proto,
                                                   host_and_port,
                                                   next_page_link)
        else:
            LOGGER.warning('Unimplemented scheme in '
                           'next_page_link %s',
                           next_page_link)

    return next_page_link


def ftr_process(url=None, content=None, config=None, base_url=None):
    """ process an URL, or some already fetched content from a given URL.

    :param url: The URL of article to extract. Can be
        ``None``, but only if you provide both ``content`` and
        ``config`` parameters.
    :type url: str, unicode or ``None``

    :param content: the HTML content already downloaded. If given,
        it will be used for extraction, and the ``url`` parameter will
        be used only for site config lookup if ``config`` is not given.
        Please, only ``unicode`` to avoid charset errors.
    :type content: unicode or ``None``

    :param config: if ``None``, it will be looked up from ``url`` with as
        much love and AI as possible. But don't expect too much.
    :type config: a :class:`SiteConfig` instance or ``None``

    :param base_url: reserved parameter, used when fetching multi-pages URLs.
        It will hold the base URL (the first one fetched), and will serve as
        base for fixing non-schemed URLs or query_string-only links to next
        page(s). Please do not set this parameter until you very know what you
        are doing. Default: ``None``.
    :type base_url: str or unicode or None

    :raises:
        - :class:`RuntimeError` in all parameters-incompatible situations.
          Please RFTD carefully, and report strange unicornic edge-cases.
        - :class:`SiteConfigNotFound` if no five-filter site config can
          be found.
        - any raw ``requests.*`` exception, network related, if anything
          goes wrong during url fetching.

    :returns:
        - either a :class:`ContentExtractor` instance with extracted
          (and :attr:`.failures`) attributes set, in case a site config
          could be found.
          When the extractor knows how to handle multiple-pages articles,
          all pages contents will be extracted and cleaned — if relevant —
          and concatenated into the instance :attr:`body` attribute.
          The :attr:`next_page_link` attribute will be a ``list``
          containing all sub-pages links. Note: the first link is the one
          you fed the extractor with ; it will not be repeated in the list.
        - or ``None``, if content was not given and url fetching returned
          a non-OK HTTP code, or if no site config could be found (in that
          particular case, no extraction at all is performed).
    """

    if url is None and content is None and config is None:
        raise RuntimeError('At least one of url or the couple content/config '
                           'argument must be present.')

    if content is not None and url is None and config is None:
        raise RuntimeError('Passing content only will not give any result.')

    if content is None:
        if url is None:
            raise RuntimeError('When content is unset, url must be set.')

        try:
            result = requests_get(url)

            if result.status_code != requests.codes.ok:
                LOGGER.error('Wrong status code in return while getting '
                             '“%s”.', url)
                return None

            LOGGER.info('Downloaded %s bytes as %s text.',
                        len(result.text), result.encoding)

            # result.text is always unicode
            content = result.text

        except Exception as e:
            LOGGER.error('Content could not be fetched from URL %s.', url)
            LOGGER.WARN(e)
            raise

    if config is None:
        # This can eventually raise SiteConfigNotFound
        config_string, matched_host = ftr_get_config(url)
        config = SiteConfig(site_config_text=config_string, host=matched_host)

    extractor = ContentExtractor(config)

    if base_url is None:
        base_url = url

    if extractor.process(html=content):

        # This is recursive. Yeah.
        if extractor.next_page_link is not None:

            next_page_link = sanitize_next_page_link(extractor.next_page_link,
                                                     base_url)

            next_extractor = ftr_process(url=next_page_link,
                                         base_url=base_url)

            extractor.body += next_extractor.body

            extractor.next_page_link = [next_page_link]

            if next_extractor.next_page_link is not None:
                extractor.next_page_link.extend(next_extractor.next_page_link)

        return extractor

    return None
