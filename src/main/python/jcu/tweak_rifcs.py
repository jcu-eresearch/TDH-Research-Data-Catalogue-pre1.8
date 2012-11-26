#JCU RIF-CS Pre-Processor
#Copyright (C) 2012  Nigel Bajema, James Cook University
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
    name = os.path.split(path)[1]

    tree = ET.parse(path)


    if name.startswith("party_"):
        #fix_party(tree)
        return
    elif name.startswith("collection_"):
        fix_collection(tree)
    elif name.startswith("activity_"):
        fix_activity(tree)
    else:
        raise Exception("Unknown Type")

    out_path = path
    if output:
        out_path = os.path.join(output, name)

    tree.write(out_path, encoding='utf-8')

def fix_party(tree): pass
def fix_activity(tree): pass
def fix_collection(tree):
    subjects = tree.xpath( "/rif:registryObjects/rif:registryObject/rif:collection/rif:subject", namespaces=namespace)
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
    emails = "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:electronic[@type='email']"
    for email in tree.xpath(emails, namespaces=namespace):
        fix_email(email)

    addr = "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:physical[@type='streetAddress']"
    for addresses in tree.xpath(addr, namespaces=namespace):
        fix_land_address(addresses)

    related = tree.xpath("/rif:registryObjects/rif:registryObject", namespaces=namespace)
    ex = ET.SubElement(related[0], "DATA_MANAGEMENT")
    ex.attrib['size'] = "0"
    ex.attrib['period'] = "0"

    relatedInfo = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedInfo", namespaces=namespace)
    for rl in relatedInfo:
        fix_relatedInfo(rl)

def fix_email(email):
    value = email.xpath("rif:value", namespaces=namespace)[0]
    eml =  value.text.strip()
    eml = eml.replace("Email: ","")
    value.text = eml
    r = requests.get(solrFieldQuery("Email", eml))
    solrResponse = json.loads(r.text)
    if solrResponse['response']['numFound'] > 1:
        raise Exception("More than one email address: "+eml)

    entry = solrResponse['response']['docs'][0]
    email.attrib['hon'] = entry['Honorific'][0]
    email.attrib['givenName'] = entry['Given_Name'][0]
    email.attrib['familyName'] = entry['Family_Name'][0]


def fix_land_address(addresses):
    ad = addresses.xpath("rif:addressPart[@type='addressLine']", namespaces=namespace)
    address = "\n".join([i.text.strip() for i in ad]).strip()
    map(lambda a: addresses.remove(a), ad)
    el = ET.SubElement(addresses, "addressPart")
    el.attrib['type'] = "combined"
    el.text = address

uri_types = {
      "http://creativecommons.org/licenses":"license",
      "http://opendatacommons.org/licenses":"license"
}

uri_keys = uri_types.keys()

def fix_relatedInfo(rel):
    id = rel.xpath("rif:identifier", namespaces=namespace)[0]
    id.attrib['uritype'] = 'url'
    val = id.text.strip()
    if id.attrib.has_key('type'):
        if id.attrib['type'] == 'uri':
            for ukey in uri_keys:
                if val.startswith(ukey):
                    id.attrib['uritype'] = uri_types[ukey]
                    break



def fix_relatedObject(rel):
    relation_nodes = rel.xpath("rif:key", namespaces=namespace)
    for key_node in relation_nodes:
        key = key_node.text.strip()
        if key.startswith("jcu.edu.au/tdh/party/"):
            fix_relatedObject_Party(rel)
        elif key.startswith("jcu.edu.au/tdh/activity/"):
            fix_relatedObject_Activity(rel)
        else:
            raise Exception("Unknown Related Object Type")

def fix_relatedObject_Activity(rel):
    id_node = rel.xpath("rif:key", namespaces=namespace)[0]
    id_node.text = id_node.text.strip().replace("jcu.edu.au/tdh/activity/", "jcu.edu.au/activity/")
    r = requests.get(solrFieldQuery("dc_identifier", id_node.text))
    solrResponse = json.loads(r.text)
    if solrResponse['response']['numFound'] == 1:
        entry = solrResponse['response']['docs'][0]
        rel.attrib['title'] = entry['dc_title']
        rel.attrib['grantNumber'] = id_node.text.replace("jcu.edu.au/activity/","")
        print id_node.text.replace("jcu.edu.au/activity/","")


def fix_relatedObject_Party(rel):
    id_node = rel.xpath("rif:key", namespaces=namespace)
    relation_node = rel.xpath("rif:relation", namespaces=namespace)
    id = id_node[0].text.strip()
    r = requests.get(user_query % id)
    solrResponse = json.loads(r.text)


    if solrResponse['response']['numFound'] != 1:
        return
    entry = solrResponse['response']['docs'][0]
    id_node[0].text=entry['dc_identifier'][0]
    fields = ["Family_Name", "Given_Name", "Honorific", "dc_title", "primary_group_id"]
    for fld in fields:

        if  isinstance(entry[fld], list):
            if len(entry[fld]) > 1:
                raise Exception("Only one element expected for: %s, got %s" % (fld, len(entry[fld])))
            rel.attrib[fld] = entry[fld][0]
        else:
            rel.attrib[fld] = entry[fld]
    id_node[0].text = entry["dc_identifier"][0]

    labels={
        "hasAssociationWith":"Associated with:",
        "hasCollector":"Aggregated by:",
        "isEnrichedBy":"Enriched by:",
        "isManagedBy":"Managed by:",
        "isOwnedBy":"Owned by:",
    }

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


