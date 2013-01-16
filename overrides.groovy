if (project.properties.containsKey("local.redbox.hostname")){
    project.properties["redbox.hostname"] = project.properties["local.redbox.hostname"]
    println "Hostname overridden to: " + project.properties["mint.hostname"]
}

if (project.properties.containsKey("redbox.project.home")){
    project.properties["project.home"] = project.properties["redbox.project.home"]
    println "Project Home overridden to: " + project.properties["project.home"]
}