init:
	(cd web; make init)

test:
	(cd test_data; ./unpack.sh)
	(cd web; make test)
