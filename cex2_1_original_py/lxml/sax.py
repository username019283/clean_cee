# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: c:\python27\lib\site-packages\lxml-3.2.4-py2.7-win32.egg\lxml\sax.py
# Compiled at: 2013-12-10 09:11:58
"""
SAX-based adapter to copy trees from/to the Python standard library.

Use the `ElementTreeContentHandler` class to build an ElementTree from
SAX events.

Use the `ElementTreeProducer` class or the `saxify()` function to fire
the SAX events of an ElementTree against a SAX ContentHandler.

See http://codespeak.net/lxml/sax.html
"""
from xml.sax.handler import ContentHandler
from lxml import etree
from lxml.etree import ElementTree, SubElement
from lxml.etree import Comment, ProcessingInstruction

class SaxError(etree.LxmlError):
    """General SAX error.
    """
    pass


def _getNsTag(tag):
    if tag[0] == '{':
        return tuple(tag[1:].split('}', 1))
    else:
        return (
         None, tag)
        return


class ElementTreeContentHandler(ContentHandler):
    """Build an lxml ElementTree from SAX events.
    """

    def __init__(self, makeelement=None):
        self._root = None
        self._root_siblings = []
        self._element_stack = []
        self._default_ns = None
        self._ns_mapping = {None: [None]}
        self._new_mappings = {}
        if makeelement is None:
            makeelement = etree.Element
        self._makeelement = makeelement
        return

    def _get_etree(self):
        """Contains the generated ElementTree after parsing is finished."""
        return ElementTree(self._root)

    etree = property(_get_etree, doc=_get_etree.__doc__)

    def setDocumentLocator(self, locator):
        pass

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, uri):
        self._new_mappings[prefix] = uri
        try:
            self._ns_mapping[prefix].append(uri)
        except KeyError:
            self._ns_mapping[prefix] = [
             uri]

        if prefix is None:
            self._default_ns = uri
        return

    def endPrefixMapping(self, prefix):
        ns_uri_list = self._ns_mapping[prefix]
        ns_uri_list.pop()
        if prefix is None:
            self._default_ns = ns_uri_list[-1]
        return

    def _buildTag(self, ns_name_tuple):
        ns_uri, local_name = ns_name_tuple
        if ns_uri:
            el_tag = '{%s}%s' % ns_name_tuple
        elif self._default_ns:
            el_tag = '{%s}%s' % (self._default_ns, local_name)
        else:
            el_tag = local_name
        return el_tag

    def startElementNS(self, ns_name, qname, attributes=None):
        el_name = self._buildTag(ns_name)
        if attributes:
            attrs = {}
            try:
                iter_attributes = attributes.iteritems()
            except AttributeError:
                iter_attributes = attributes.items()

            for name_tuple, value in iter_attributes:
                if name_tuple[0]:
                    attr_name = '{%s}%s' % name_tuple
                else:
                    attr_name = name_tuple[1]
                attrs[attr_name] = value

        else:
            attrs = None
        element_stack = self._element_stack
        if self._root is None:
            element = self._root = self._makeelement(el_name, attrs, self._new_mappings)
            if self._root_siblings and hasattr(element, 'addprevious'):
                for sibling in self._root_siblings:
                    element.addprevious(sibling)

            del self._root_siblings[:]
        else:
            element = SubElement(element_stack[-1], el_name, attrs, self._new_mappings)
        element_stack.append(element)
        self._new_mappings.clear()
        return

    def processingInstruction(self, target, data):
        pi = ProcessingInstruction(target, data)
        if self._root is None:
            self._root_siblings.append(pi)
        else:
            self._element_stack[-1].append(pi)
        return

    def endElementNS(self, ns_name, qname):
        element = self._element_stack.pop()
        el_tag = self._buildTag(ns_name)
        if el_tag != element.tag:
            raise SaxError('Unexpected element closed: ' + el_tag)

    def startElement(self, name, attributes=None):
        if attributes:
            attributes = dict([ ((None, k), v) for k, v in attributes.items() ])
        self.startElementNS((None, name), name, attributes)
        return

    def endElement(self, name):
        self.endElementNS((None, name), name)
        return

    def characters(self, data):
        last_element = self._element_stack[-1]
        try:
            last_element = last_element[-1]
            last_element.tail = (last_element.tail or '') + data
        except IndexError:
            last_element.text = (last_element.text or '') + data

    ignorableWhitespace = characters


class ElementTreeProducer(object):
    """Produces SAX events for an element and children.
    """

    def __init__(self, element_or_tree, content_handler):
        try:
            element = element_or_tree.getroot()
        except AttributeError:
            element = element_or_tree

        self._element = element
        self._content_handler = content_handler
        from xml.sax.xmlreader import AttributesNSImpl as attr_class
        self._attr_class = attr_class
        self._empty_attributes = attr_class({}, {})

    def saxify(self):
        self._content_handler.startDocument()
        element = self._element
        if hasattr(element, 'getprevious'):
            siblings = []
            sibling = element.getprevious()
            while getattr(sibling, 'tag', None) is ProcessingInstruction:
                siblings.append(sibling)
                sibling = sibling.getprevious()

            for sibling in siblings[::-1]:
                self._recursive_saxify(sibling, {})

        self._recursive_saxify(element, {})
        if hasattr(element, 'getnext'):
            sibling = element.getnext()
            while getattr(sibling, 'tag', None) is ProcessingInstruction:
                self._recursive_saxify(sibling, {})
                sibling = sibling.getnext()

        self._content_handler.endDocument()
        return

    def _recursive_saxify(self, element, prefixes):
        content_handler = self._content_handler
        tag = element.tag
        if tag is Comment or tag is ProcessingInstruction:
            if tag is ProcessingInstruction:
                content_handler.processingInstruction(element.target, element.text)
            if element.tail:
                content_handler.characters(element.tail)
            return
        new_prefixes = []
        build_qname = self._build_qname
        attribs = element.items()
        if attribs:
            attr_values = {}
            attr_qnames = {}
            for attr_ns_name, value in attribs:
                attr_ns_tuple = _getNsTag(attr_ns_name)
                attr_values[attr_ns_tuple] = value
                attr_qnames[attr_ns_tuple] = build_qname(attr_ns_tuple[0], attr_ns_tuple[1], prefixes, new_prefixes)

            sax_attributes = self._attr_class(attr_values, attr_qnames)
        else:
            sax_attributes = self._empty_attributes
        ns_uri, local_name = _getNsTag(tag)
        qname = build_qname(ns_uri, local_name, prefixes, new_prefixes)
        for prefix, uri in new_prefixes:
            content_handler.startPrefixMapping(prefix, uri)

        content_handler.startElementNS((ns_uri, local_name), qname, sax_attributes)
        if element.text:
            content_handler.characters(element.text)
        for child in element:
            self._recursive_saxify(child, prefixes)

        content_handler.endElementNS((ns_uri, local_name), qname)
        for prefix, uri in new_prefixes:
            content_handler.endPrefixMapping(prefix)

        if element.tail:
            content_handler.characters(element.tail)

    def _build_qname(self, ns_uri, local_name, prefixes, new_prefixes):
        if ns_uri is None:
            return local_name
        else:
            try:
                prefix = prefixes[ns_uri]
            except KeyError:
                prefix = prefixes[ns_uri] = 'ns%02d' % len(prefixes)
                new_prefixes.append((prefix, ns_uri))

            return prefix + ':' + local_name


def saxify(element_or_tree, content_handler):
    """One-shot helper to generate SAX events from an XML tree and fire
    them against a SAX ContentHandler.
    """
    return ElementTreeProducer(element_or_tree, content_handler).saxify()