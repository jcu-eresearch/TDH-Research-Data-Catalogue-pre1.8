if (project.properties.containsKey("local.redbox.hostname")){
    project.properties["redbox.hostname"] = project.properties["local.redbox.hostname"]
}

println "Hostname Set to: " + project.properties["redbox.hostname"]