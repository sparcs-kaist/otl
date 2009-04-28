PYTHON_SRC=     /usr/lib/python2.5

MKHOWTO=	$(PYTHON_SRC)/doc/tools/mkhowto

.PHONY: html

PAPER=		a4

DOCFILES= copyright.tex

all:	pdf

dvi:	$(DOCFILES) version
	$(MKHOWTO) --dvi sybase.tex

pdf:	$(DOCFILES) version
	$(MKHOWTO) --pdf --$(PAPER) sybase.tex

ps:	$(DOCFILES) version
	$(MKHOWTO) --ps --$(PAPER) sybase.tex

booklet: ps
	cat sybase.ps | psbook | psnup -2 | pstumble > sybase-booklet.ps

html:	$(DOCFILES) version
	$(MKHOWTO) --html sybase.tex
	mkdir -p sybase/icons
	cp $(PYTHON_SRC)/doc/html/icons/* sybase/icons/
	-rm sybase/sybase.how
# the iconserver option of mkhowto is broken since it writes
# it to the end if the init_file where they aren't useful anymore,
# so we work around it:
	for f in `find sybase`; do \
	  cat $$f | sed s/\.\.\\/icons/icons/g > $${f}2; \
	  mv $${f}2 $$f; \
	done
	-rm sybase/sybase2
	-rm sybase/icons/icons2

world:	booklet pdf html

pdf-$(PAPER).tgz: pdf
	tar cf - *.pdf | gzip -9 >$@

postscript-$(PAPER).tgz: ps
	tar cf - *.ps | gzip -9 >$@

html.tgz:	html
	tar cf - sybase | gzip -9 >$@

clean:
	rm -f *~ *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn *.pla api.tex

# HTML in the doc directory
dist: version html
	rm -rf ../doc
	mv sybase ../doc

# Version substitution
version: ../Sybase.py
	DATE="`LANG=en date +'%B %d, %Y'`"; \
	VERSION="`awk '/__version__/ {print $$3}' ../Sybase.py`"; \
	VERSION="`echo $$VERSION | sed s/\\'//g`"; \
	cat sybase.tex | sed s/\\release.*/\\release\{$$VERSION\}/ >sybase.tex2; \
	cat sybase.tex2 | sed s/\\date.*/\\date\{"$$DATE"\}/ >sybase.tex
