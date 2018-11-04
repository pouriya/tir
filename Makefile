.PHONY: install uninstall


install:
	python3 setup.py install
	chmod a+x ./tir/tir.py
	ln -s $$PWD/tir/tir.py /usr/local/bin/tir

uninstall:
	rm -rf /usr/local/bin/tir
