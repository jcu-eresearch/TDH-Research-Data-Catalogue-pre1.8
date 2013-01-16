if(project.properties.containsKey("redbox.project.home")){
    project.properties["project.home"] =  project.properties["redbox.project.home"];
}
String projectHome = project.properties["project.home"];
if (projectHome == null) {
    String userHome = System.getProperty("user.home");
    File redboxHome = new File(new File(userHome, "deployment"), "redbox");
    project.properties["project.home"] = redboxHome.absolutePath;
    new File(redboxHome, "system").mkdirs();
}
ph = new File(".project-home")
ph.write(project.properties["project.home"])

project.properties["app.location.linux"] =   project.properties["project.home"];
project.properties["app.location.windows"] = project.properties["project.home"];

println "Project will be deployed to: " + project.properties["project.home"];


java.net.InetAddress address = InetAddress.getByName(System.getenv("COMPUTERNAME"));
project.properties["ip.address"] = address.getHostAddress();
println "Computer IP Address: " + project.properties["ip.address"];


project.properties["server.url.base"] = project.properties["redbox.hostname"]+"/"+project.properties["redbox.context"]
