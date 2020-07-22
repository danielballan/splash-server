import pytest
import mongomock

from splash.data.base import MongoCollectionDao, BadIdError


@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


def test_crud_compounds(mongodb):
    mongo_crud_service = MongoCollectionDao(mongodb, 'compounds')
    compound = dict(name='boron')
    uid = mongo_crud_service.create(compound)
    assert uid is not None
    retrieved_compound = mongo_crud_service.retrieve(uid)
    assert retrieved_compound['uid'] == uid
    assert retrieved_compound['name'] == 'boron'

    # test update
    compound['name'] = 'dilithium crystals'
    mongo_crud_service.update(compound)
    retrieved_compound = mongo_crud_service.retrieve(uid)
    assert retrieved_compound['name'] == 'dilithium crystals'

    # test that you get error updating doc with no id
    bad_compound = {'name': 'foo'}
    with pytest.raises(BadIdError):
        mongo_crud_service.update(bad_compound)

    # test delete
    mongo_crud_service.delete(retrieved_compound['uid'])
    assert mongo_crud_service.retrieve(uid) is None


def test_create_indexes(mongodb):
    dao = TestDao(mongodb, 'great_collection')
    collection = dao._collection
    indexes = list(collection.list_indexes())
    assert len(indexes) == 2  # default _id index plus ours
    assert indexes[1]['key']['foo'] == 1


class TestDao(MongoCollectionDao):
    def __init__(self, db, collection):
        super().__init__(db, collection)

    def _collection_setup(self):
        self._collection.create_index([
            ('foo', 1)
        ])
