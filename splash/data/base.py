import logging
# from bson.objectid import ObjectId
# from bson.errors import InvalidId
import uuid

db = None


class Dao(object):
    '''Interface for CRUD Serverice'''

    def create(self, doc):
        raise NotImplementedError

    def retrive(self, uid):
        raise NotImplementedError

    def retreive_many(self, query=None):
        raise NotImplementedError

    def update(self, doc):
        raise NotImplementedError

    def delete(self, uid):
        raise NotImplementedError


class MongoCollectionDao(Dao):
    ''' Mongo data service for mapping CRUD and search
    operations to a MongoDB. '''
    def __init__(self, collection):
        self.collection = collection

    def create(self, doc):
        logging.debug(f"create doc in collection {0}, doc: {1}", self.collection, doc)
        uid = uuid.uuid4()
        doc['uid'] = str(uid)
        self.collection.insert_one(doc)
        return doc['uid']

    def retrieve(self, uid):
        return self.collection.find_one({"uid": uid})

    def retrieve_multiple(self, page, query=None, page_size=10):
        if query is None:
            # Calculate number of documents to skip
            skips = page_size * (page - 1)
            num_results = self.collection.find().count()
            # Skip and limit
            cursor = self.collection.find().skip(skips).limit(page_size)

            # Return documents
            return num_results, cursor

        else:
            raise NotImplementedError

    def update(self, doc):
        # update should not be able to change uid
        if 'uid' not in doc:
            raise BadIdError('Cannot change object uid')
        # update_one might be more efficient, but kinda tricky
        status = self.collection.replace_one({"uid": doc['uid']}, doc)
        if status.modified_count == 0:
            raise ObjectNotFoundError

    def delete(self, uid):
        status = self.collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError



class ObjectNotFoundError(Exception):
    pass


class BadIdError(Exception):
    pass