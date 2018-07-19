# Development

To develop features or fix bugs in this project, a `Makefile` is available in
order to help the setup of the environment and the testing of the templates

# Setting up the virtualenv

Since this is at python2.7 project for now, first one needs to ensure
the `virtualenv` module is installed in the system-wide python. This *make
target* helps with this part, and *sudo* might be necessary since packages
would be installed in the system's python

```
sudo make virtualenv-requirements
```

From now on, packages installations/configs/tests will be done in the
*virtualenv* (not system-wide), therefore *sudo* isn't needed (this is why
the previous step is done separately). So, now the *virtualenv* can be created:

```
make virtualenv
```

Now activate the *virtualenv*, which unfortunately cannot easily be added to
the Makefile since *Make* creates sanitized sub-shells for each command, and
our parent shell doesn't get the environment variables that the *virtualenv*
setups up on activation:

```
source virtualenv/bin/activate
```

Install the development requirements

```
make development
```


# Cleaning up the *virtualenv*

First *deactivate* the *virtualenv*

```
deactivate
```

Cleanup the *virtualenv*, python bytcode cache, and temporary files:

```
make clean-all
```

To **Only** cleanup the tmp/cache files (keeping the *virtualenv* and the
installed requirements):

```
make clean
```
