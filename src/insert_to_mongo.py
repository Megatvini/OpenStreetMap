from audit_and_fix import fixed_data_iterator
from pymongo import MongoClient
from tqdm import tqdm


def main():
    mongo_db = MongoClient()['OpenStreetMap']
    collection_names = {
        'node': 'Nodes',
        'way': 'Ways',
        'relation': 'Relations'
    }

    for data in tqdm(fixed_data_iterator()):
        elem_type = data['elem_tag']
        collection_name = collection_names[elem_type]
        mongo_db[collection_name].insert(data)


if __name__ == '__main__':
    main()
