CRAWLER = $(CURDIR)/bin/crawler.py
EXE = /usr/local/bin/tir

.PHONY: install uninstall


install: uninstall
	python3 setup.py install
	chmod a+x $(CRAWLER)
	ln -s $(CRAWLER) $(EXE)

uninstall:
	rm -rf $(EXE)
