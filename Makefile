install:
	sudo pip install -U -r requirements.txt
	sudo pip install .

check_convention:
	pep8 treepicker

clean:
	rm -rf AUTHORS build ChangeLog *.egg-info
