INDEXES = site/eta_car_periastron_2014/index.html \
					site/wr71/index.html \
					site/u_tra/index.html

ZIPS = site/eta_car_periastron_2014.zip \
			 site/wr71.zip \
			 site/u_tra.zip

all: $(INDEXES) $(ZIPS)

clean:
	rm -f $(INDEXES) $(ZIPS)

site/%.zip: site/%/fits/*
	rm -f $@
	zip -r -j $@ $^

site/%/index.html: site/%/fits/*
	chmod 644 site/$*/fits/*
	./generate.py $*

sync:
	rsync -vax site/ bollo:websites/saser.wholemeal.co.nz/
