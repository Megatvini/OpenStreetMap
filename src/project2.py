from collections import defaultdict
from datetime import datetime
import xml.etree.ElementTree as ET

FILE_NAME = 'sample.osm'


def fix_types(data):
    data['id'] = int(data['id'])
    if 'visible' in data:
        data['visible'] = data['visible'] == 'true'
    data['version'] = int(data['version'])
    data['changeset'] = int(data['changeset'])
    data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    data['uid'] = int(data['uid'])
    data['lat'] = float(data['uid'])
    data['lon'] = float(data['uid'])

    if 'nodes' in data:
        data['nodes'] = list(map(int, data['nodes']))
    return data


def parse_elem_node_or_way(elem, tree):
    elem_tag = elem.tag
    attributes = elem.attrib
    children = defaultdict(list)

    while True:
        event, elem = next(tree)
        if (event, elem.tag) == ('end', elem_tag):
            break
        if event == 'start':
            children[elem.tag].append(elem.attrib)

    elem_data = {'type': elem_tag}

    for tag in children['tag']:
        key, value = tag['k'], tag['v']
        elem_data[key] = value

    if len(children['nd']) > 0:
        elem_data['nodes'] = [x['ref'] for x in children['nd']]

    elem_data = {**attributes, **elem_data}
    elem_data = fix_types(elem_data)
    return elem_data


def parse_elems(elem, tree):
    if elem.tag in ['node', 'way']:
        yield parse_elem_node_or_way(elem, tree)
    else:
        while next(tree)[0] != 'end':
            pass


def parse_all_elems(tree):
    while True:
        try:
            event, elem = next(tree)
            if event == 'start':
                yield from parse_elems(elem, tree)
        except StopIteration:
            break


def main():
    tree = ET.iterparse(FILE_NAME, events=('start', 'end'))
    for data in parse_all_elems(tree):
        print(data)


if __name__ == '__main__':
    main()
