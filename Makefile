all: eta_car wr71 u_tra

eta_car:
	chmod 644 site/eta_car_periastron_2014/fits/*
	./generate.py eta_car_periastron_2014 'Eta Carinae periastron campaign 2014'
	rm -f site/eta_car_periastron_2014.zip
	zip -r -j site/eta_car_periastron_2014.zip site/eta_car_periastron_2014/fits/

wr71:
	chmod 644 site/wr71/fits/*
	./generate.py wr71 'WR71'
	rm -f site/wr71.zip
	zip -r -j site/wr71.zip site/wr71/fits/

u_tra:
	chmod 644 site/u_tra/fits/*
	./generate.py u_tra 'U TrA'
	rm -f site/u_tra.zip
	zip -r -j site/u_tra.zip site/u_tra/fits/

sync:
	rsync -vax site/ bollo:websites/saser.wholemeal.co.nz/
