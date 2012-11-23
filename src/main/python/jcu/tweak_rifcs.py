
from lxml import etree as ET

import requests
import json, urllib
import os.path

mint_protocol = "http"
mint_host = "localhost:9001"

mint_url = "{protocol}://{mint_host}/solr/fascinator".format(protocol=mint_protocol, mint_host=mint_host)

anzsrc_query = '{base_url}/select?wt=json&q=dc_identifier%%3D"{query}"'.format(base_url=mint_url, query="%s")

dc_i_query = '{base_url}/select?wt=json&q=dc_identifier%%3D"{query}"'.format(base_url=mint_url, query="%s")

user_query = '{base_url}/select?wt=json&q=known_ids%%3D"{query}"'.format(base_url=mint_url, query="%s")

field_query = '{base_url}/select?wt=json&q={field}%3A{value}'

#ET._namespace_map["http://ands.org.au/standards/rif-cs/registryObjects"] = "rif"

namespace={"rif":"http://ands.org.au/standards/rif-cs/registryObjects"}

def solrFieldQuery(field, value):
    return field_query.format(base_url=mint_url, field=field, value=urllib.quote(value, safe=''))

def fix(path, args, output):
    tree = ET.parse(path)
    root = tree.getroot()
    subjects = tree.xpath( "/rif:registryObjects/rif:registryObject/rif:collection/rif:subject", namespaces=namespace)
    print subjects
    for subject in subjects:
        if subject.attrib.has_key("type"):
            if subject.attrib['type'] == 'anzsrc-for':
                orig = subject.text.strip()
                subject.text = "http://purl.org/asc/1297.0/2008/for/" + orig
                subject.attrib['title'] = getTitle(subject.text, orig)
            if subject.attrib['type'] == 'anzsrc-seo':
                orig = subject.text.strip()
                subject.text = "http://purl.org/asc/1297.0/2008/seo/" + orig
                subject.attrib['title'] = getTitle(subject.text, orig)

    related = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedObject", namespaces=namespace)
    for rel in related:
        fix_relatedObject(rel)
    addr = "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:physical[@type='streetAddress']"

    for addresses in tree.xpath(addr, namespaces=namespace):
        ad = addresses.xpath("rif:addressPart[@type='addressLine']", namespaces=namespace)
        address = "\n".join([i.text.strip() for i in ad]).strip()
        map(lambda a: addresses.remove(a), ad)
        el = ET.SubElement(addresses, "addressPart")
        el.attrib['type'] = "combined"
        el.text = address

    related = tree.xpath("/rif:registryObjects/rif:registryObject", namespaces=namespace)
    ex = ET.SubElement(related[0], "DATA_MANAGEMENT")
    ex.attrib['size'] = "0"
    ex.attrib['period'] = "0"

    out_path = path
    if output:
        out_path = os.path.join(output, os.path.split(path)[1])

    print "OUT PATH", out_path
    tree.write(out_path, encoding='utf-8')


def fix_relatedObject(rel):
    id_node = rel.xpath("rif:key", namespaces=namespace)
    relation_node = rel.xpath("rif:relation", namespaces=namespace)
    id = id_node[0].text.strip()
    r = requests.get(user_query % id)
    solrResponse = json.loads(r.text)


    if solrResponse['response']['numFound'] != 1:
        return
    entry = solrResponse['response']['docs'][0]
    fields = ["Family_Name", "Given_Name", "Honorific", "dc_title", "primary_group_id"]
    for fld in fields:

        if  isinstance(entry[fld], list):
            if len(entry[fld]) > 1:
                raise Exception("Only one element expected for: %s, got %s" % (fld, len(entry[fld])))
            rel.attrib[fld] = entry[fld][0]
        else:
            rel.attrib[fld] = entry[fld]
    id_node[0].text = entry["dc_identifier"][0]
    labels={"hasAssociationWith":"Associated with:", "isManagedBy":"Managed By:", "hasCollector":""}
    relation_node[0].attrib['label'] = labels[relation_node[0].attrib['type']]

    r = requests.get(solrFieldQuery("dc_identifier", entry["primary_group_id"][0]))
    orgu_res = json.loads(r.text.encode("utf-8"))
    rel.attrib["primary_group_name"] = orgu_res['response']['docs'][0]["Name"][0]


def getTitle(id, orig):
    r = requests.get(anzsrc_query % id)
    solrResponse = json.loads(r.text)
    for val in solrResponse['response']['docs']:
        if id in val['dc_identifier']:
            return "%s - %s (%s)" % (orig, val['dc_title'], orig)


