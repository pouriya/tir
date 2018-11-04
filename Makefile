.PHONY: install uninstall


install:
	chmod a+x ./tir/tir.py
	ln -s $(CURDIR)/tir/tir.py /usr/local/bin/tir

uninstall:
	rm -rf /usr/local/bin/tir
