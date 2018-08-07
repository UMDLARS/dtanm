init:
	(cd scorer_server; make init)

test:
	(cd test_data; ./unpack.sh)
	(cd scorer_server; make test)
