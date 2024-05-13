run-playbook:
	ansible-playbook -i hosts.ini playbook.yml --extra-vars "app_version=$(V)"

deploy/deps/init:
	pip install pip-tools

deploy/deps/compile:
	pip-compile

deploy/deps/install:
	pip-sync
