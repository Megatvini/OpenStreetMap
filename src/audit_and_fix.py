from parse_osm import all_elems_iterator
import re


def is_number(param):
    try:
        int(param)
    except:
        return False
    return True


def fix_max_speed(data):
    max_speed = data['maxspeed']
    if max_speed == 'none':
        del data['maxspeed']
    if is_number(max_speed):
        number = int(max_speed)
        if number < 10:
            data['maxspeed'] = number * 10
    return data


street_pattern = re.compile('(( St\.)|( st\.)|( St)|( st)|( Str\.)|( str\.)|( Str)|( str)|( street))$')
street_pattern_geo = re.compile('( ქ.\$)|( ქ$)')
avenue_pattern = re.compile('( Ave\.$)|( ave\.$)|( Ave$)|( ave$)')
avenue_pattern_geo = re.compile('( გამზ\.$)|( გამზ$)')


def fix_street_address(street):
    street = street_pattern.sub(' Street', street)
    street = street_pattern_geo.sub(' ქუჩა', street)
    street = avenue_pattern.sub(' გამზირი', street)
    street = avenue_pattern_geo.sub(' Avenue', street)
    return street


def fixed(data):
    if 'maxspeed' in data:
        data = fix_max_speed(data)
    if 'addr:street' in data:
        data['addr:street'] = fix_street_address(data['addr:street'])

    return data


def fixed_data_iterator():
    for data in all_elems_iterator():
        yield fixed(data)


def main():
    speeds = set()
    streets = set()
    for data in fixed_data_iterator():
        if 'addr:street' in data:
            streets.add(data['addr:street'])
        if 'maxspeed' in data:
            speeds.add(data['maxspeed'])
    print(speeds)
    print(streets)


if __name__ == '__main__':
    main()
