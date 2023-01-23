APP_PORT := 5001

dev:
	pipenv run env \
		FLASK_APP=app \
		flask --debug run --port $(APP_PORT)

shell:
	pipenv run env \
		FLASK_APP=app \
		flask --debug shell

test:
	pipenv run \
		pytest --verbose --no-header tests/

test-debug:
	pipenv run \
		pytest --verbose --no-header --pdb tests/

clean:
	killall -u $(USER) flask || true
	rm -rvf instance/
