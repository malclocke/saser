INDEXES = site/eta_car_periastron_2014/index.html \
					site/wr71/index.html \
					site/zet_pup/index.html \
					site/gamma-2_vel/index.html \
					site/u_tra/index.html \
					site/alp_tra/index.html \
					site/wr6/index.html \
					site/uw_cma/index.html \
					site/mu_sgr/index.html \
					site/hd139966/index.html

ZIPS = site/eta_car_periastron_2014.zip \
			 site/wr71.zip \
			 site/gamma-2_vel.zip \
			 site/zet_pup.zip \
			 site/u_tra.zip \
			 site/alp_tra.zip \
			 site/wr6.zip \
			 site/uw_cma.zip \
			 site/mu_sgr.zip \
			 site/hd139966.zip

PLOTS := $(patsubst %,%.png,$(wildcard site/*/fits/*.fit))
THUMBS := $(patsubst %,%.thumb.png,$(wildcard site/*/fits/*.fit))

all: site/index.html site/policy.html $(INDEXES) $(ZIPS) $(PLOTS) $(THUMBS)

site/index.html: templates/index.html templates/base.html
	./generate_static.py index.html site/index.html

site/policy.html: templates/policy.html templates/base.html
	./generate_static.py policy.html site/policy.html

clean:
	rm -f $(INDEXES) $(ZIPS)

site/%.zip: site/%/fits/*.fit
	rm -f $@
	zip -r -j $@ $^

site/%/index.html: site/%/fits/* templates/*.html
	chmod 644 site/$*/fits/*
	./generate.py $*

sync:
	rsync -vax site/ vince:websites/saser.wholemeal.co.nz/

publish: sync

%.thumb.png: %
	./plot_image.py --compact --width 50 --height 50 $< $@

%.png: %
	./plot_image.py $< $@
