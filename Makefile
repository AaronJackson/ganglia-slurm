
all:
	cp conf.d/*.pyconf /etc/ganglia/conf.d/
	cp python_modules/*.py /usr/lib64/ganglia/python_modules/
