INDEXES = site/eta_car_periastron_2014/index.html \
					site/wr71/index.html \
					site/zet_pup/index.html \
					site/u_tra/index.html

ZIPS = site/eta_car_periastron_2014.zip \
			 site/wr71.zip \
			 site/zet_pup.zip \
			 site/u_tra.zip

PLOTS := $(patsubst %,%.png,$(wildcard site/*/fits/*.fit))
THUMBS := $(patsubst %,%.thumb.png,$(wildcard site/*/fits/*.fit))

all: site/index.html $(INDEXES) $(ZIPS) $(PLOTS) $(THUMBS)

site/index.html: templates/index.html templates/base.html
	./generate_static.py index.html site/index.html

clean:
	rm -f $(INDEXES) $(ZIPS)

site/%.zip: site/%/fits/*.fit
	rm -f $@
	zip -r -j $@ $^

site/%/index.html: site/%/fits/* templates/campaign.html templates/base.html
	chmod 644 site/$*/fits/*
	./generate.py $*

sync:
	rsync -vax site/ bollo:websites/saser.wholemeal.co.nz/

%.thumb.png: %
	./plot_image.py --compact --width 50 --height 50 $< $@

%.png: %
	./plot_image.py $< $@
