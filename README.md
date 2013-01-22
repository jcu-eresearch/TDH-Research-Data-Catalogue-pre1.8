TDH-Research-Data-Catalogue
===========================
This repository contains the Jame Cook University RedBoX Institutional build.
After running mvn install on mint, ReDBoX, fascinator-shibboleth, and plugin-harvester-directoryName:

	#> mvn -Dproject.home=<deploy.directory> package

If you do not define project.home then it defaults to $HOME/deployment/redbox.

System Setup
============
Once you have deployed the institutional build you will need to setup the init symlinks.

Redhat
------
    #> cd /etc/init.d
    #> ln -s <deploy.directory>/system/redhat/init redbox
    #> cd /etc/sysconfig
    #> ln -s <deploy.directory>/system/redhat/redbox redbox
    #> cd /var/log
    #> ln -s <deploy.directory>/home/logs redbox

Then edit /etc/sysconfig/redbox and set the `USER` variable.


Development
===========

During development it is often handy to have a profile in your settings.xml that 
redbox into your target directory, like such:

                <profile>
                    <id>deployment_location</id>
                    <properties>
                        <redbox.project.home>${project.build.directory}/deploy</redbox.project.home>
                    </properties>
                </profile>
                <profile>
                    <id>dev_hostname</id>
                    <properties>
                        <local.redbox.hostname>http://redbox.dev.hostname:${server.port}</local.redbox.hostname>
                    </properties>
                </profile>

You just activate this profile in your IDE when you are working on it.
Alternatively, you can activate the profile with the `activeProfiles` section of ~/.m2/settings.xml
