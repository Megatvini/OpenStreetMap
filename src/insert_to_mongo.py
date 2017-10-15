from audit_and_fix import fixed_data_iterator
from pymongo import MongoClient
from tqdm import tqdm


def main():
    mongo_db = MongoClient()['OpenStreetMap']
    for data in tqdm(fixed_data_iterator()):
        mongo_db['Elements'].insert(data)


if __name__ == '__main__':
    main()
