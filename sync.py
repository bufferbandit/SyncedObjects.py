from shared_memory_dict import SharedMemoryDict


class SyncObject(SharedMemoryDict):
	# Check if object is the oldest object
	@property
	def is_eldest(self):
		return self.id == min(self.get("registered_client_ids", []))

	def __init__(self, size=1024, prefix="SyncedObject__", *args, **kwargs):
		# Set the name of the "channel" to the class name
		self.name = prefix + self.__class__.__name__
		super().__init__(name=self.name, size=size, *args, **kwargs)
		registered_client_ids = self.get("registered_client_ids", [])
		# Create an id that is current max id + 1
		self.id = 0 if not registered_client_ids else (max(registered_client_ids) + 1)
		# "register" the id (by just adding it to the list)
		registered_client_ids.append(self.id)
		self.__setitem__("registered_client_ids", registered_client_ids)

	# When calling "del" on the object, remove the id from the ids
	def __del__(self):
		registered_client_ids = self["registered_client_ids"]
		del self["registered_client_ids"]

		registered_client_ids.remove(self.id)
		self["registered_client_ids"] = registered_client_ids

		super().__del__()

	def __setattr__(self, key, value):
		# If item is in this set, set the item as an attribute (practically do not sync it)
		#  otherwise set it to the (synced) dict
		if key in {"_serializer", "_memory_block", "id", "name"}:
			super().__setattr__(key, value)
		else:
			super().__setitem__(key, value)

	def __getattr__(self, item):
		# If it is an existing attribute return that attr otherwise return the item from the dict
		return existing_item if (existing_item := self.__dict__.get(item, None)) else super().__getitem__(item)


class Client(SyncObject):
	supported_methods = ["get", "post"]
	def __init__(self, *args, **kwargs):
		SyncObject.__init__(self)
		if self.is_eldest:
			self.timeout = 3600




if __name__ == "__main__":
	client1 = Client()
	client1.token = "aaa.bbb.ccc"
	print(f"{client1.token=}")
	print(f"{dict(client1)=}")



	client2 = Client()
	print(f"{client2.token=}")
	print(f"{dict(client2)=}")

	assert(client1.token == client2.token)


	del client1
	print(client2)
