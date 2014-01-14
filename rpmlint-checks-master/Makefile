LIBDIR=/usr/share/rpmlint

PYTHON = python

DEFAULT = *.py
EXPERIMENTAL = experimental/*.py
OBSOLETE = obsolete/*.py
TEST = test/*/*.spec

all: default experimental obsolete

default:
	if [ "x${COMPILE_PYC}" = "x1" ] ; then \
		$(PYTHON) -m py_compile *.py ; \
	fi
	$(PYTHON) -O -m py_compile *.py

experimental:
	if [ "x${COMPILE_PYC}" = "x1" ] ; then \
		$(PYTHON) -m py_compile $(EXPERIMENTAL) ; \
	fi
	$(PYTHON) -O -m py_compile $(EXPERIMENTAL)

obsolete:
	if [ "x${COMPILE_PYC}" = "x1" ] ; then \
		$(PYTHON) -m py_compile $(OBSOLETE) ; \
	fi
	$(PYTHON) -O -m py_compile $(OBSOLETE)

clean:
	rm -f *~ *.pyc *.pyo
	rm -f experimemntal/*~ experimental/*.pyc experimental/*.pyo
	rm -f obsolete/*~ obsolete/*.pyc obsolete/*.pyo

install: all
	mkdir -p $(DESTDIR)$(LIBDIR)/experimental
	mkdir -p $(DESTDIR)$(LIBDIR)/obsolete
	-cp -p *.pyc $(DESTDIR)$(LIBDIR)
	cp -p *.py *.pyo $(DESTDIR)$(LIBDIR)
	-cp -p experimental/*.pyc $(DESTDIR)$(LIBDIR)/experimental
	cp -p experimental/*.py experimental/*.pyo $(DESTDIR)$(LIBDIR)/experimental
	-cp -p obsolete/*.pyc $(DESTDIR)$(LIBDIR)/obsolete
	cp -p obsolete/*.py obsolete/*.pyo $(DESTDIR)$(LIBDIR)/obsolete

.PHONY: all clean experimental install obsolete

