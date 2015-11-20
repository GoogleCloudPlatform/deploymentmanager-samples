Creates a set of VMs running Salt master and minions.

Demonstrates templates in Jinja and Python.

After the resources are created, you need to SSH into the master and run this
command to accept the keys:
`sudo salt-key -A`

Then (still on the master) you can test the set-up by running:
`sudo salt '*' test.ping`

If this works, create directory `/srv/salt` on the master and copy to it
`top.sls`, `webserver.sls` and `index.html` from the states folder.
Then run:
`sudo salt '*' state.highstate`

You should now be able to go to the external IP of one of the minions
and see "Hello world!".
