String projectHome = project.properties["project.home"];
if (projectHome == null) {
    String userHome = System.getProperty("user.home");
    File redboxHome = new File(new File(userHome, "deployment"), "redbox");
    project.properties["project.home"] = redboxHome.absolutePath;
    new File(redboxHome, "system").mkdirs();
}
println "Project will be deployed to: " + project.properties["project.home"];

java.net.InetAddress address = InetAddress.getByName(System.getenv("COMPUTERNAME"));
project.properties["ip.address"] = address.getHostAddress();
println "Computer IP Address: " + project.properties["ip.address"];
