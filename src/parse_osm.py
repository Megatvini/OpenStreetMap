from collections import defaultdict
from datetime import datetime
import xml.etree.ElementTree as ET

FILE_NAME = 'tbilisi.osm'


def fix_types(data):
    data['id'] = int(data['id'])
    data['version'] = int(data['version'])
    data['changeset'] = int(data['changeset'])
    data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    data['uid'] = int(data['uid'])

    if 'visible' in data:
        data['visible'] = data['visible'] == 'true'
    if 'lat' in data:
        data['lat'] = float(data['lat'])
    if 'lon' in data:
        data['lon'] = float(data['lon'])
    if 'nodes' in data:
        data['nodes'] = list(map(int, data['nodes']))
    if 'ways' in data:
        data['ways'] = list(map(int, data['ways']))
    return data


def parse_elem(elem, iterator):
    elem_tag = elem.tag
    attributes = elem.attrib
    children = defaultdict(list)

    while True:
        # advancing iterator until current element ends
        event, elem = next(iterator)
        if (event, elem.tag) == ('end', elem_tag):
            break
        if event == 'start':
            children[elem.tag].append(elem.attrib)

    elem_data = {'elem_tag': elem_tag}

    # accumulate all the data including attributes and tags in one dictionary
    for tag in children['tag']:
        key, value = tag['k'], tag['v']
        elem_data[key] = value

    # save node references
    if len(children['nd']) > 0:
        elem_data['nodes'] = [x['ref'] for x in children['nd']]

    # save members if its a relation
    if len(children['member']) > 0:
        nodes = []
        ways = []
        for member in children['member']:
            if member['type'] == 'node':
                nodes.append(member['ref'])
            elif member['type'] == 'way':
                ways.append(member['ref'])
        elem_data['nodes'] = nodes
        elem_data['ways'] = ways

    elem_data = {**attributes, **elem_data}
    elem_data = fix_types(elem_data)
    return elem_data


def parse_elems(elem, iterator):
    if elem.tag in ['node', 'way', 'relation']:
        yield parse_elem(elem, iterator)
    else:
        while next(iterator)[0] != 'end':
            pass


def parse_all_elems(iterator):
    while True:
        try:
            event, elem = next(iterator)
            if event == 'start':
                yield from parse_elems(elem, iterator)
        except StopIteration:
            break


def all_elems_iterator():
    """
    parses nodes, ways and relations
    :return: generator for all parsed elements
    """
    iterator = ET.iterparse(FILE_NAME, events=('start', 'end'))
    return parse_all_elems(iterator)
