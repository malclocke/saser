all: eta_car

eta_car:
	chmod 644 site/eta_car_periastron_2014/fits/*
	./generate.py eta_car_periastron_2014 'Eta Carinae periastron campaign 2014'
	rm -f site/eta_car_periastron_2014.zip
	zip -r -j site/eta_car_periastron_2014.zip site/eta_car_periastron_2014/fits/

sync:
	rsync -vax site/ bollo:websites/saser.wholemeal.co.nz/
