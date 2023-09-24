run_tests:
	python -m unittest discover

run_test:
	python -m unittest tests.test_http_server

start_server:
	python http_server/http_server.py