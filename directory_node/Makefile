dev:
	pipenv run env \
		FLASK_APP=app \
		flask --debug run

shell:
	pipenv run env \
		FLASK_APP=app \
		flask --debug shell

test:
	pipenv run python tests/api_test.py

clean:
	killall -u $(USER) flask || true
	rm -rvf instance/
