#
# Rules script for sample directory Names data
#
import time
import urllib
import httplib

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.common import FascinatorHome

from java.lang import Exception
from java.lang import String
from java.util import HashSet

from org.apache.commons.io import IOUtils

class IndexData:
    def __init__(self):
        pass

    def __activate__(self, context):
        # Prepare variables
        self.index = context["fields"]
        self.indexer = context["indexer"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]
        self.config = context["jsonConfig"]
        self.log = context["log"]
        self.redboxVersion = self.config.getString("", "redbox.version.string")
        
        # Common data
        self.__newDoc()
        self.packagePid = None
        pidList = self.object.getPayloadIdList()
        for pid in pidList:
            if pid.endswith("metadata.json"):
                self.packagePid = pid

        # Real metadata
        if self.itemType == "object":
            self.__basicData()
            self.__metadata()

        # Make sure security comes after workflows
        self.__security()

    def __newDoc(self):
        self.oid = self.object.getId()
        self.pid = self.payload.getId()
        metadataPid = self.params.getProperty("metaPid", "DC")

        self.utils.add(self.index, "storage_id", self.oid)
        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.utils.add(self.index, "identifier", self.pid)

        self.utils.add(self.index, "id", self.oid)
        self.utils.add(self.index, "item_type", self.itemType)
        self.utils.add(self.index, "last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.utils.add(self.index, "harvest_config", self.params.getProperty("jsonConfigOid"))
        self.utils.add(self.index, "harvest_rules",  self.params.getProperty("rulesOid"))

        self.item_security = []
        self.owner = self.params.getProperty("owner", "admin")
        
    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])
        # Persistent Identifiers
        pidProperty = self.config.getString(None, ["curation", "pidProperty"])
        if pidProperty is None:
            self.log.error("No configuration found for persistent IDs!")
        else:
            pid = self.params[pidProperty]
            if pid is not None:
                self.utils.add(self.index, "known_ids", pid)
                self.utils.add(self.index, "pidProperty", pid)
                self.utils.add(self.index, "oai_identifier", pid)
        self.utils.add(self.index, "oai_set", "Directory_Names")
        # Publication
        published = self.params["published"]
        if published is not None:
            self.utils.add(self.index, "published", "true")

    def __metadata(self):

        self.__checkMetadataPayload()

        jsonPayload = self.object.getPayload("metadata.json")
        json = self.utils.getJsonObject(jsonPayload.open())
        jsonPayload.close()

        metadata = json.getObject("metadata")

        identifier  = metadata.get("dc.identifier")
        self.utils.add(self.index, "dc:identifier", identifier)
        self.utils.add(self.index, "known_ids", identifier)
        self.__storeIdentifier(identifier)
        self.utils.add(self.index, "institution", "James Cook University")
        self.utils.add(self.index, "source", "http://spatialecology.jcu.edu.au/Edgar/")
                
        data = json.getObject("data")

        ####Global setting for processing data
        ####These will need to be changed based on you system installation.
        theMintHost = "http://localhost:9001"
        redboxHost  = "localhost:9000"
        collectionRelationTypesFilePath = FascinatorHome.getPath() + "/../portal/default/redbox/workflows/forms/data/"

        ###Using the species name, obtained from the directory name, to replace the text in the Title
        species = data.get("species")
        title = data.get("title")
        title = title.replace("%NAME_OF_FOLDER%", species)
        self.utils.add(self.index, "dc_title", title)
        self.utils.add(self.index, "dc:title", title)

        self.utils.add(self.index, "dc_type", data.get("type"))
        self.utils.add(self.index, "dc:type", data.get("type"))
        self.utils.add(self.index, "dc:created", time.strftime("%Y-%m-%d", time.gmtime()))
        self.utils.add(self.index, "dc:modified", "")
        self.utils.add(self.index, "dc:language", "")
        self.utils.add(self.index, "dc:coverage.vivo:DateTimeInterval.vivo:start", data.get("temporalCoverage").get("dateFrom"))
        self.utils.add(self.index, "dc:coverage.vivo:DateTimeInterval.vivo:end", data.get("temporalCoverage").get("dateTo"))
        self.utils.add(self.index, "dc:coverage.redbox:timePeriod", "")

        ###Processing the 'spatialCoverage' metadata.
        spatialCoverage = data.get("spatialCoverage")
        for i in range(len(spatialCoverage)):
            location = spatialCoverage[i]
            if  location["type"] == "text":
                self.utils.add(self.index, "dc:coverage.vivo:GeographicLocation." + str(i) + ".type", location["type"])
                self.utils.add(self.index, "dc:coverage.vivo:GeographicLocation." + str(i) + ".redbox:wktRaw", location["value"])
                self.utils.add(self.index, "dc:coverage.vivo:GeographicLocation." + str(i) + ".rdf:PlainLiteral", location["value"])

        ###Processing the 'description' metadata.
        description = data.get("description")
        for i in range(len(description)):
            desc = description[i]
            tempDesc = desc.get("value")
            tempDesc = tempDesc.replace("%NAME_OF_FOLDER%", species)
            if  i == 0:
                self.utils.add(self.index, "dc:description", tempDesc)
            self.utils.add(self.index, "rif:description." + str(i) + ".type", desc["type"])
            self.utils.add(self.index, "rif:description." + str(i) + ".value", tempDesc)

        ###Processing the 'relatedPublication' metadata
        relatedPublication = data.get("relatedPublication")
        if relatedPublication is not None:
            for i in range(len(relatedPublication)):
                publication = relatedPublication[i]
                self.utils.add(self.index, "dc:relation.swrc:Publication." + str(i) + ".dc:identifier", publication["url"])
                self.utils.add(self.index, "dc:relation.swrc:Publication." + str(i) + ".dc:title", publication["title"])

        ###Processing the 'relatedWebsite' metadata
        relatedWebsite = data.get("relatedWebsite")
        count = 0
        for i in range(len(relatedWebsite)):
            website = relatedWebsite[i]
            self.utils.add(self.index, "dc:relation.bibo:Website." + str(i) + ".dc:identifier" , website["url"])
            self.utils.add(self.index, "dc:relation.bibo:Website." + str(i) + ".dc:title" , website["notes"])
            count = i

        ###Processing the 'data_source_website' metadata (override metadata)
        dataSourceWebsites = data.get("data_source_website")
        if  dataSourceWebsites is not None:
            for i in range(len(dataSourceWebsites)):
                website = dataSourceWebsites[i]
                type = website.get("identifier").get("type")
                if type == "uri":
                    count += 1 
                    self.utils.add(self.index, "dc:relation.bibo:Website." + str(count) + ".dc:identifier" , website.get("identifier").get("value"))
                    self.utils.add(self.index, "dc:relation.bibo:Website." + str(count) + ".dc:title" , website["notes"])

        ###Processing the 'relatedCollection' metadata
        #Reading the file here, so we only do it once.
        file = open(collectionRelationTypesFilePath + "collectionRelationTypes.json")
        collectionData = file.read()
        file.close()
        relatedCollection = data.get("relatedCollection")
        for i in range(len(relatedCollection)):
            collection = relatedCollection[i]
            tempIdentifier = collection["identifier"]
            if tempIdentifier is not None:
                tempIdentifier = tempIdentifier.replace("%NAME_OF_FOLDER%", species)
            else:
                tempIdentifier = ""
            self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".dc:identifier", tempIdentifier)
            tempTitle = collection.get("title")
            tempTitle = tempTitle.replace("%NAME_OF_FOLDER%", species)
            self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".dc:title", tempTitle)
            self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".vivo.Relationship.rdf.PlainLiteral", collection["relationship"])
            self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".redbox:origin", "on")
            self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".redbox:publish", "on")
            #Using the collection data as a lookup to obtain the 'label'
            relationShip = collection.get("relationship")
            jsonSimple = JsonSimple(collectionData)
            jsonObj = jsonSimple.getJsonObject()
            results = jsonObj.get("results")
            #ensuring the Collection Relation Types exist
            if  results:
                for j in range(len(results)):
                    relation = results[j]
                    if  (relationShip == relation.get("id")):
                        self.utils.add(self.index, "dc:relation.vivo:Dataset." + str(i) + ".vivo.Relationship.skos:prefLabel", relation.get("label"))

        ###Processing the 'associatedParty' metadata
        associatedParty = data.get("associatedParty")
        for i in range(len(associatedParty)):
            party = associatedParty[i]
            email = party.get("who").get("value")
            if email is not None:
                #Using the email address to obtain the Party details from The Mint
                #For testing, hard coded email address
                #email = "paul.james@example.edu.au"
                sock = urllib.urlopen(theMintHost + "/mint/default/opensearch/lookup?count=999&searchTerms=Email:" + email)
                mintData = sock.read()
                sock.close()
                jsonSimple = JsonSimple(mintData)
                jsonObj = jsonSimple.getJsonObject()
                results = jsonObj.get("results")
                #Ensuring that the Email identified a Party from The Mint
                if  results:
                    resultMetadata = JsonObject(results.get(0))
                    allData = resultMetadata.get("result-metadata")
                    creator = allData.get("all")
                    whoType = party.get("who").get("type")
                    if ((creator is not None) and (whoType == 'people')):
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".dc:identifier", creator.get("dc:identifier")[0])
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".foaf:name", creator.get("dc:title"))
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".foaf:title", creator.get("Honorific")[0])
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".redbox:isCoPrimaryInvestigator", "off")
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".redbox:isPrimaryInvestigator", "on")
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".foaf:givenName", creator.get("Given_Name")[0])
                        self.utils.add(self.index, "dc:creator.foaf:Person." + str(i) + ".foaf:familyName", creator.get("Family_Name")[0])
                        self.utils.add(self.index, "dc:creator", creator.get("Given_Name")[0] + " " + creator.get("Family_Name")[0])                        

        ###Processing 'contactInfo.email' metadata
        contactInfoEmail = data.get("contactInfo").get("email")
        #Using the email address to obtain details from The Mint
        #For testing, hard coded email address
        #contactInfoEmail = "paul.james@example.edu.au"
        sock = urllib.urlopen(theMintHost + "/mint/default/opensearch/lookup?count=999&searchTerms=Email:" + contactInfoEmail)
        mintData = sock.read()
        sock.close()
        jsonSimple = JsonSimple(mintData)
        jsonObj = jsonSimple.getJsonObject()
        results = jsonObj.get("results")
        #Ensuring that the Email identified a Party from The Mint
        if  results:
            resultMetadata = JsonObject(results.get(0))
            allData = resultMetadata.get("result-metadata")
            creator = allData.get("all")
            if (creator is not None):
                self.utils.add(self.index, "locrel:prc.foaf:Person.dc:identifier", creator.get("dc:identifier").toString())
                self.utils.add(self.index, "locrel:prc.foaf:Person.foaf:name", creator.get("dc:title"))
                self.utils.add(self.index, "locrel:prc.foaf:Person.foaf:title", creator.get("Honorific").toString())
                self.utils.add(self.index, "locrel:prc.foaf:Person.foaf:givenName", creator.get("Given_Name").toString())
                self.utils.add(self.index, "locrel:prc.foaf:Person.foaf:familyName", creator.get("Family_Name").toString())

        ###Processing 'coinvestigators' metadata
        coinvestigators = data.get("coinvestigators")
        for i in range(len(coinvestigators)):
            self.utils.add(self.index, "dc:contributor.loclrel:clb." + str(i) + ".foaf:Agent" , coinvestigators[i])            

        ###Processing 'anzsrcFOR' metadata
        anzsrcFOR = data.get("anzsrcFOR")
        for i in range(len(anzsrcFOR)):
            anzsrc = anzsrcFOR[i]
            #Querying against The Mint, but only using the first 4 numbers from anzsrc, this ensure a result
            sock = urllib.urlopen(theMintHost + "/mint/ANZSRC_FOR/opensearch/lookup?count=999&level=http://purl.org/asc/1297.0/2008/for/" + anzsrc[:4])
            mintData = sock.read()
            sock.close()
            jsonSimple = JsonSimple(mintData)
            jsonObj = jsonSimple.getJsonObject()
            results = jsonObj.get("results")      
            #ensuring that anzsrc identified a record in The Mint
            if  results:
                for j in range(len(results)):
                    result = JsonObject(results.get(j))
                    rdfAbout = result.get("rdf:about")
                    target = "http://purl.org/asc/1297.0/2008/for/" + anzsrc
                    if  (rdfAbout == target):
                        self.utils.add(self.index, "dc:subject.anzsrc:for." + str(i) + ".skos:prefLabel" , result.get("skos:prefLabel"))            
                        self.utils.add(self.index, "dc:subject.anzsrc:for." + str(i) + ".rdf:resource" , rdfAbout)            

        ###Processing 'anzsrcSEO' metadata                        
        anzsrcSEO = data.get("anzsrcSEO")
        for i in range(len(anzsrcSEO)):
            anzsrc = anzsrcSEO[i]
            #Querying against The Mint, but only using the first 4 numbers from anzsrc, this ensure a result
            sock = urllib.urlopen(theMintHost + "/mint/ANZSRC_SEO/opensearch/lookup?count=999&level=http://purl.org/asc/1297.0/2008/seo/" + anzsrc[:4])
            mintData = sock.read()
            sock.close()
            jsonSimple = JsonSimple(mintData)
            jsonObj = jsonSimple.getJsonObject()
            results = jsonObj.get("results")      
            #ensuring that anzsrc identified a record in The Mint
            if  results:
                for j in range(len(results)):
                    result = JsonObject(results.get(j))
                    rdfAbout = result.get("rdf:about")
                    target = "http://purl.org/asc/1297.0/2008/seo/" + anzsrc
                    if  (rdfAbout == target):
                        self.utils.add(self.index, "dc:subject.anzsrc:seo." + str(i) + ".skos:prefLabel" , result.get("skos:prefLabel"))            
                        self.utils.add(self.index, "dc:subject.anzsrc:seo." + str(i) + ".rdf:resource" , rdfAbout)            

        ###Processing 'keyword' metadata                        
        keyword = data.get("keyword")
        print("Jay keyword: " + keyword.toString())
        self.utils.add(self.index, "keywords", keyword.toString())
        for i in range(len(keyword)):
            self.utils.add(self.index, "dc:subject.vivo:keyword." + str(i) + ".rdf:PlainLiteral", keyword[i])

        self.utils.add(self.index, "dc:accessRights.skos:prefLabel", data.get("accessRights"))
        self.utils.add(self.index, "dc:license.dc:identifier", data.get("license").get("url"))
        self.utils.add(self.index, "dc:license.skos:prefLabel", data.get("license").get("label"))
        self.utils.add(self.index, "dc:identifier.redbox:origin", "internal")

        dataLocation = data.get("dataLocation")
        dataLocation = dataLocation.replace("%NAME_OF_FOLDER%", species)
        self.utils.add(self.index, "bibo:Website.1.dc:identifier", dataLocation)

        #The following have been intentionally set to blank. No mapping is required for these fields.
        self.utils.add(self.index, "vivo:Location", "")
        self.utils.add(self.index, "redbox:retentionPeriod", data.get("retentionPeriod"))
        self.utils.add(self.index, "dc:extent", "unknown")
        self.utils.add(self.index, "redbox:disposalDate", "")
        self.utils.add(self.index, "locrel:own.foaf:Agent.1:foaf_name", "")
        self.utils.add(self.index, "locrel:dtm.foaf:Agent.foaf_name", "")

        ###Processing 'organizationalGroup' metadata
        organisationalGroup = data.get("organizationalGroup")
        for i in range(len(organisationalGroup)):
            organisation = organisationalGroup[i]
            #Querying against The Mint
            sock = urllib.urlopen(theMintHost + "/mint/Parties_Groups/opensearch/lookup?count=9999&searchTerms=ID:" + organisation)
            mintData = sock.read()
            sock.close()
            jsonSimple = JsonSimple(mintData)
            jsonObj = jsonSimple.getJsonObject()
            results = jsonObj.get("results")      
            #ensuring that anzsrc identified a record in The Mint
            if  results:
                resultMetadata = JsonObject(results.get(0))
                allData = resultMetadata.get("result-metadata")
                orgGroup = allData.get("all")
                self.utils.add(self.index, "foaf:Organization.dc:identifier", orgGroup.get("dc_identifier")[0])
                self.utils.add(self.index, "foaf:Organization.skos:prefLabel", orgGroup.get("Name")[0])

        self.utils.add(self.index, "foaf:fundedBy.foaf:Agent", "")
        self.utils.add(self.index, "foaf:fundedBy.vivo:Grant", "")
        self.utils.add(self.index, "swrc:ResearchProject.dc:title", "")
        self.utils.add(self.index, "locrel:dpt.foaf:Person.foaf:name", "")
        self.utils.add(self.index, "dc:SizeOrDuration", "")
        self.utils.add(self.index, "dc:Policy", "")
        self.utils.add(self.index, "redbox:ManagementPlan", "")

        self.__workflow()
    
    def __security(self):
        # Security
        roles = self.utils.getRolesWithAccess(self.oid)
        if roles is not None:
            # For every role currently with access
            for role in roles:
                # Should show up, but during debugging we got a few
                if role != "":
                    if role in self.item_security:
                        # They still have access
                        self.utils.add(self.index, "security_filter", role)
                    else:
                        # Their access has been revoked
                        self.__revokeAccess(role)
            # Now for every role that the new step allows access
            for role in self.item_security:
                if role not in roles:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.utils.add(self.index, "security_filter", role)

        # No existing security
        else:
            if self.item_security is None:
                # Guest access if none provided so far
                self.__grantAccess("guest")
                self.utils.add(self.index, "security_filter", role)
            else:
                # Otherwise use workflow security
                for role in self.item_security:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.utils.add(self.index, "security_filter", role)
        # Ownership
        if self.owner is None:
            self.utils.add(self.index, "owner", "system")
        else:
            self.utils.add(self.index, "owner", self.owner)

    def __grantAccess(self, newRole):
        schema = self.utils.getAccessSchema("derby");
        schema.setRecordId(self.oid)
        schema.set("role", newRole)
        self.utils.setAccessSchema(schema, "derby")

    def __revokeAccess(self, oldRole):
        schema = self.utils.getAccessSchema("derby");
        schema.setRecordId(self.oid)
        schema.set("role", oldRole)
        self.utils.removeAccessSchema(schema, "derby")

    def __indexList(self, name, values):
        for value in values:
            self.utils.add(self.index, name, value)

    def __workflow(self):
        # Workflow data
        WORKFLOW_ID = "dataset"
        wfChanged = False
        workflow_security = []
        self.message_list = None
        stages = self.config.getJsonSimpleList(["stages"])
        if self.owner == "guest":
            pageTitle = "Submission Request"
            displayType = "submission-request"
            initialStep = 0
        else:
            pageTitle = "Metadata Record"
            displayType = "package-dataset"
            initialStep = 1

        print("Jay: stages[0]: " + stages[0].toString())
        print("Jay: stages[1]: " + stages[1].toString())
        print("Jay: stages[2]: " + stages[2].toString())
        print("Jay: stages[3]: " + stages[3].toString())
        print("Jay: stages[4]: " + stages[4].toString())
        print("Jay: stages[5]: " + stages[5].toString())
        print("Jay: pageTitle: " + pageTitle)
        print("Jay: displayType: " + displayType)
        print("Jay: initialStep: " + str(initialStep))

        try:
            wfMeta = self.__getJsonPayload("workflow.metadata")
            wfMeta.getJsonObject().put("pageTitle", pageTitle)

            print("Jay: workflow.metadata exists")

            # Are we indexing because of a workflow progression?
            targetStep = wfMeta.getString(None, ["targetStep"])
            if targetStep is not None and targetStep != wfMeta.getString(None, ["step"]):
                wfChanged = True
                # Step change
                wfMeta.getJsonObject().put("step", targetStep)
                wfMeta.getJsonObject().remove("targetStep")
            # This must be a re-index then
            else:
                targetStep = wfMeta.getString(None, ["step"])

            # Security change
            for stage in stages:
                if stage.getString(None, ["name"]) == targetStep:
                    wfMeta.getJsonObject().put("label", stage.getString(None, ["label"]))
                    self.item_security = stage.getStringList(["visibility"])
                    workflow_security = stage.getStringList(["security"])
                    if wfChanged == True:
                        self.message_list = stage.getStringList(["message"])
        except StorageException:
            # No workflow payload, time to create
            
            print("Jay: exception: creating workflow.metadata")

            initialStage = stages.get(initialStep).getString(None, ["name"])
            wfChanged = True
            wfMeta = JsonSimple()
            wfMetaObj = wfMeta.getJsonObject()
            wfMetaObj.put("id", WORKFLOW_ID)
            wfMetaObj.put("step", initialStage)
            wfMetaObj.put("pageTitle", pageTitle)
            stages = self.config.getJsonSimpleList(["stages"])
            for stage in stages:
                if stage.getString(None, ["name"]) == initialStage:
                    wfMetaObj.put("label", stage.getString(None, ["label"]))
                    self.item_security = stage.getStringList(["visibility"])
                    workflow_security = stage.getStringList(["security"])
                    self.message_list = stage.getStringList(["message"])

        print("Jay: wfMetaObj: " + wfMetaObj.toString())
        print("Jay: wfChanged: " + str(wfChanged))

        # Has the workflow metadata changed?
        if wfChanged == True:
            inStream = IOUtils.toInputStream(wfMeta.toString(True), "UTF-8")
            try:
                StorageUtils.createOrUpdatePayload(self.object, "workflow.metadata", inStream)
                print("Jay: added workflow.metadata to payload")                
            except StorageException:        
                print("Jay: exception workflow.metadata not added")
                print(" ERROR updating dataset payload")

        #Date must be of the format "%Y-%m-%dT%H:%M:%SZ" for the Solr Index
        self.utils.add(self.index, "date_created", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))                            
        self.utils.add(self.index, "display_type", displayType)

        # Workflow processing
        wfStep = wfMeta.getString(None, ["step"])
        self.utils.add(self.index, "workflow_id", wfMeta.getString(None, ["id"]))
        self.utils.add(self.index, "workflow_step", wfStep)
        self.utils.add(self.index, "workflow_step_label", wfMeta.getString(None, ["label"]))
        for group in workflow_security:
            self.utils.add(self.index, "workflow_security", group)
            if self.owner is not None:
                self.utils.add(self.index, "workflow_security", self.owner)
        # set OAI-PMH status to deleted
        if wfStep == "retired":
            self.utils.add(self.index, "oai_deleted", "true")

    def __getJsonPayload(self, pid):
        payload = self.object.getPayload(pid)
        json = self.utils.getJsonObject(payload.open())
        payload.close()
        return json

    def __storeIdentifier(self, identifier):
        try:
            # Where do we find persistent IDs?
            pidProperty = self.config.getString("persistentId", ["curation", "pidProperty"])
            metadata = self.object.getMetadata()
            storedId = metadata.getProperty(pidProperty)
            if storedId is None:
                metadata.setProperty(pidProperty, identifier)
                # Make sure the indexer triggers a metadata save afterwards
                self.params["objectRequiresClose"] = "true"
        except Exception, e:
            self.log.info("Error storing identifier against object: ", e)

    def __checkMetadataPayload(self):
        try:
            # Simple check for its existance
            self.object.getPayload("formData.tfpackage")
            self.firstHarvest = False
        except Exception:
            self.firstHarvest = True
            # We need to create it
            self.log.info("Creating 'formData.tfpackage' payload for object '{}'", self.oid)
            # Prep data
            data = {
                "viewId": "default",
                "workflow_source": "Edgar Import",
                "packageType": "dataset",
                "redbox:formVersion": self.redboxVersion,
                "redbox:newForm": "true"
            }
            print("Jay formData.tfpackage: " + str(data))
            package = JsonSimple(JsonObject(data))
            # Store it
            inStream = IOUtils.toInputStream(package.toString(True), "UTF-8")
            try:
                self.object.createStoredPayload("formData.tfpackage", inStream)
                self.packagePid = "formData.tfpackage"
            except StorageException, e:
                self.log.error("Error creating 'formData.tfpackage' payload for object '{}'", self.oid, e)
                raise Exception("Error creating package payload: ", e)