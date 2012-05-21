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

Then edit /etc/sysconfig/redbox and set the `USER` variable.


Development
===========

During development it is often handy to have a profile in your settings.xml that deploys
redbox into your target directory, like such:

            <profile>
                <id>jcu_institutional_build_dev</id>
                <properties>
                    <project.home>${project.build.directory}/deploy</project.home>
                </properties>
            </profile>

You just activate this profile in your IDE when you are working on it.