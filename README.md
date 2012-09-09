TDH-Research-Data-Catalogue
===========================
This repository contains the Jame Cook University RedBoX Institutional build.
After running mvn install on mint and ReDBoX:

	#> mvn -Dproject.home=<deploy.directory> package

If you do not define project.home then is defaults to $HOME/jcu-redbox.

During development it is often handy to have a profile in your settings.xml that deploys
redbox into your target directory, like such:

            <profile>
                <id>jcu_institutional_build_dev</id>
                <properties>
                    <project.home>${project.build.directory}/deploy</project.home>
                </properties>
            </profile>

You just activate this profile in your IDE when you are working on it.