init:
	(cd scorer; make init)

test:
	(cd test_data; ./unpack.sh)
	(cd scorer; make test)
