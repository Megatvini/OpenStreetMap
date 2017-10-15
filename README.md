# OpenStreetMap Sample Project Data Wrangling with MongoDB


## Map Area
[Tbilisi](https://www.openstreetmap.org/relation/4479704), [Georgia](https://www.openstreetmap.org/relation/28699)

For exploration I chose the city of Tbilisi the reason being that it is my hometown. There were couple problems with the data which I managed to improve

## Problems with the data

1. **Node Type** - Some nodes have tags with k=type which would overwrite {'type': 'node'} attribute in output json file
2. **Spelling Speed Limits** - Misspelled (single digit) speed limits on some roads
3. **Street Name Abbreviations** - Street name abbreviations both in English and Georgian (Marjanishvili st., მარჯანიშვილის ქ.)

### **Node Type**
The easiest fix was to just use different name to denote type of the element 
```python
def parse_elem(elem, iterator):
    elem_tag = elem.tag
    elem_data = {'elem_tag': elem_tag}
    ...
```

### **Spelling Speed Limits**
There are 3 basic cases of `max_speed` values:
1. `number`, it is obvious misspelling when its single digit
2. `none`, this might mean that there is no limit at all, but I know for a fact that all the rodes have speed limits in Tbilisi, so there is not point in saving this value.
3. `number; number` meaning different limits for different parts of the road, Leaving it as is
```python
def is_number(text):
    try:
        int(text)
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
...
```
### **Street Name Abbreviations**
The abbreviations here were both in English and Georgian at the end of names. I replaced all the different versions of abbreviations with full word 
`Street` in Georgian is `ქუჩა`
`Avenue` in Georgian is `გამზირი`
```python
import re
...
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
...
```

## Overview of the data

### Size of the file
Exported data in xml format was 110 megabytes
Tbilisi.osm  -------------------- 110mb

### number of documents
\> db.Elements.count()      
603670

### number of nodes:
\> db.Elements.find({'elem_tag': 'node'}).count()
544064

### number of ways:
\> db.Elements.find({'elem_tag': 'way'}).count()
58837

### number of unique users:
\> db.Elements.distinct('user').length      
1314

### number of different nodes
Top 10 different types of nodes
```javascript
db.Elements.aggregate([
{'$match': {'elem_tag': 'node'}},
{
    '$group': {
       '_id': '$amenity',
       'count': {'$sum': 1}
    }
}, 
{'$sort': {'count': -1}},
{'$limit': 10}
])
```
```javascript
[{"_id" : null, "count" : 540804.0},
{"_id" : "restaurant", "count" : 412.0},
{"_id" : "pharmacy", "count" : 299.0},
{"_id" : "fuel", "count" : 232.0},
{"_id" : "cafe", "count" : 230.0},
{"_id" : "place_of_worship", "count" : 203.0},
{"_id" : "atm", "count" : 199.0},
{"_id" : "bank", "count" : 192.0},
{"_id" : "school", "count" : 162.0},
{"_id" : "car_wash", "count" : 117.0}]
```
This result was no surprise for my, except maybe pharmacies which turned out to be much more than I expected

### number of entries per year
Lets see the most active years
```javascript
db.Elements.aggregate([
{
    '$match': {'elem_tag': 'node'}
},
{
    '$group': {
       '_id': {'year': {'$year': "$timestamp"}},
       'count': {'$sum': 1}
    }
}, 
{
    '$sort': {'count': -1}
}])
```
```javascript
[
{"_id": {"year": 2010}, "count": 181844.0},
{"_id": {"year": 2011}, "count": 67169.0},
{"_id": {"year": 2012}, "count": 61239.0},
{"_id": {"year": 2016}, "count": 48824.0},
{"_id": {"year": 2014}, "count": 48757.0},
{"_id": {"year": 2017}, "count": 42483.0},
{"_id": {"year": 2015}, "count": 38813.0},
{"_id": {"year": 2013}, "count": 33778.0},
{"_id": {"year": 2009}, "count": 14386.0},
{"_id": {"year": 2008}, "count": 6771.0}
]
```
So, 2010 was by far the most active year in terms of new entries and it has been relatively low in past years. However this might not be negative thing, because it could be caused by the data becoming relatively complete


