import mock


class MockBuyer(object):

    def __init__(self):
        self.get = mock.Mock(side_effect=self.grab)
        self.post = mock.Mock(side_effect=self.replace)
        self.buyers = {}
        self.id_counter = 0

    def __call__(self, id):
        self.id = id
        return self

    def grab(self, uuid, *args, **kwargs):
        if uuid in self.buyers:
            return self.buyers[uuid]
        return {}

    def replace(self, data):
        uuid = data['uuid']
        if uuid not in self.buyers:
            data['resource_pk'] = self.id_counter
            self.id_counter += 1
        self.buyers[uuid] = data
        return {}


class MockGeneric(object):
    def __init__(self):
        self.buyer = MockBuyer()
        self.verify_pin = mock.Mock()
        self.confirm_pin = mock.Mock()


class MockSlumber(object):
    def __init__(self):
        self.generic = MockGeneric()
