#
# Rules script for sample directory Names data
#
import time
import urllib
import httplib
import java, os

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
            if pid.endswith(".tfpackage"):
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
        self.title = None
        self.dcType = None

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
        theMintHost = java.lang.System.getProperty("mint.proxy.url")
        collectionRelationTypesFilePath = FascinatorHome.getPath() + "/../portal/default/redbox/workflows/forms/data/"
        descriptionTypesFilePath = FascinatorHome.getPath() + "/../portal/default/local/workflows/forms/data/"

        ###Allocating space to create the formData.tfpackage
        tfpackageData = {}

        ###Using the species name, obtained from the directory name, to replace the text in the Title
        species = data.get("species")
        title = data.get("title")
        title = title.replace("%NAME_OF_FOLDER%", species)
        self.utils.add(self.index, "dc_title", title)
        tfpackageData["dc:title"] = title
        tfpackageData["title"] = title

        self.utils.add(self.index, "dc_type", data.get("type"))
        tfpackageData["dc:type.rdf:PlainLiteral"] = data.get("type")
        tfpackageData["dc:type.skos:prefLabel"] = data.get("type")
        tfpackageData["dc:created"] = time.strftime("%Y-%m-%d", time.gmtime())
        tfpackageData["dc:modified"] = ""
        self.utils.add(self.index, "dc_language", "English")
        tfpackageData["dc:language.skos:prefLabel"] = "English"
        tfpackageData["dc:coverage.vivo:DateTimeInterval.vivo:start"] = data.get("temporalCoverage").get("dateFrom")
        
        dateTo = data.get("temporalCoverage").get("dateTo")
        if dateTo is not None:
            tfpackageData["dc:coverage.vivo:DateTimeInterval.vivo:end"] = dateTo
        
        tfpackageData["dc:coverage.redbox:timePeriod"] = ""

        ###Processing the 'spatialCoverage' metadata.
        spatialCoverage = data.get("spatialCoverage")
        for i in range(len(spatialCoverage)):
            location = spatialCoverage[i]
            if  location["type"] == "text":
                tfpackageData["dc:coverage.vivo:GeographicLocation." + str(i + 1) + ".dc:type"] = location["type"]
                if  (location["value"].startswith("POLYGON")):
                    tfpackageData["dc:coverage.vivo:GeographicLocation." + str(i + 1) + ".redbox:wktRaw"] = location["value"]
                tfpackageData["dc:coverage.vivo:GeographicLocation." + str(i + 1) + ".rdf:PlainLiteral"] = location["value"]

        ###Processing the 'description' metadata.
        #Reading the file here, so we only do it once.
        file = open(descriptionTypesFilePath + "descriptionTypes.json")
        descriptionData = file.read()
        file.close()
        description = data.get("description")
        for i in range(len(description)):
            desc = description[i]
            tempDesc = desc.get("value")
            tempDesc = tempDesc.replace("%NAME_OF_FOLDER%", species)
            if  (desc["type"] == "brief"):
                tfpackageData["dc:description"] = tempDesc
            tfpackageData["rif:description." + str(i + 1) + ".type"] = desc["type"]
            tfpackageData["rif:description." + str(i + 1) + ".value"] = tempDesc
            jsonSimple = JsonSimple(descriptionData)
            jsonObj = jsonSimple.getJsonObject()
            results = jsonObj.get("results")
            #ensuring the Description Type exist
            if  results:
                for j in range(len(results)):
                    descriptionType = results[j]
                    if  (desc["type"] == descriptionType.get("id")):
                        tfpackageData["rif:description." + str(i + 1) + ".label"] = descriptionType.get("label")

        ###Processing the 'relatedPublication' metadata
        relatedPublication = data.get("relatedPublication")
        if relatedPublication is not None:
            for i in range(len(relatedPublication)):
                publication = relatedPublication[i]
                tfpackageData["dc:relation.swrc:Publication." + str(i + 1) + ".dc:identifier"] = publication["doi"]
                tfpackageData["dc:relation.swrc:Publication." + str(i + 1) + ".dc:title"] = publication["title"]

        ###Processing the 'relatedWebsite' metadata
        relatedWebsite = data.get("relatedWebsite")
        count = 0
        for i in range(len(relatedWebsite)):
            website = relatedWebsite[i]
            tfpackageData["dc:relation.bibo:Website." + str(i + 1) + ".dc:identifier"] = website["url"]
            tfpackageData["dc:relation.bibo:Website." + str(i + 1) + ".dc:title"] = website["notes"]
            count = i + 1

        ###Processing the 'data_source_website' metadata (override metadata)
        dataSourceWebsites = data.get("data_source_website")
        if  dataSourceWebsites is not None:
            for i in range(len(dataSourceWebsites)):
                website = dataSourceWebsites[i]
                type = website.get("identifier").get("type")
                if type == "uri":
                    count += 1 
                    tfpackageData["dc:relation.bibo:Website." + str(count) + ".dc:identifier"] = website.get("identifier").get("value")
                    tfpackageData["dc:relation.bibo:Website." + str(count) + ".dc:title"] = website["notes"]

        ###Processing the 'relatedCollection' metadata
        #Reading the file here, so we only do it once.
        file = open(collectionRelationTypesFilePath + "collectionRelationTypes.json")
        collectionData = file.read()
        file.close()
        relatedCollection = data.get("relatedCollection")
        recordIdentifier = ""
        for i in range(len(relatedCollection)):
            collection = relatedCollection[i]
            tempIdentifier = collection["identifier"]
            if tempIdentifier is not None:
                tempIdentifier = tempIdentifier.replace("%NAME_OF_FOLDER%", species)
                recordIdentifier = tempIdentifier
            else:
                tempIdentifier = ""
            tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".dc:identifier"] = tempIdentifier
            tempTitle = collection.get("title")
            tempTitle = tempTitle.replace("%NAME_OF_FOLDER%", species)
            tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".dc:title"] = tempTitle
            tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".vivo:Relationship.rdf:PlainLiteral"] = collection["relationship"]
            if  tempIdentifier == "":
                tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".redbox:origin"] = "on"
            tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".redbox:publish"] =  "on"
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
                        tfpackageData["dc:relation.vivo:Dataset." + str(i + 1) + ".vivo:Relationship.skos:prefLabel"] = relation.get("label")

        ###Processing the 'associatedParty' metadata
        associatedParty = data.get("associatedParty")
        for i in range(len(associatedParty)):
            party = associatedParty[i]
            email = party.get("who").get("value")
            if email is not None:
                #Using the email address to obtain the Party details from The Mint
                #For testing, hard coded email address
                #email = "paul.james@example.edu.au"
                sock = urllib.urlopen(theMintHost + "/default/opensearch/lookup?count=999&searchTerms=Email:" + email)
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
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".dc:identifier"] = creator.get("dc_identifier")[0]
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".foaf:name"] = creator.get("dc_title")
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".foaf:title"] = creator.get("Honorific")[0]
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".redbox:isCoPrimaryInvestigator"] = "off"
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".redbox:isPrimaryInvestigator"] = "on"
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".foaf:givenName"] = creator.get("Given_Name")[0]
                        tfpackageData["dc:creator.foaf:Person." + str(i + 1) + ".foaf:familyName"] = creator.get("Family_Name")[0]

        ###Processing 'contactInfo.email' metadata
        contactInfoEmail = data.get("contactInfo").get("email")
        #Using the email address to obtain details from The Mint
        #For testing, hard coded email address
        #contactInfoEmail = "paul.james@example.edu.au"
        sock = urllib.urlopen(theMintHost + "/default/opensearch/lookup?count=999&searchTerms=Email:" + contactInfoEmail)
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
                tfpackageData["locrel:prc.foaf:Person.dc:identifier"] = creator.get("dc:identifier").toString()
                tfpackageData["locrel:prc.foaf:Person.foaf:name"] = creator.get("dc:title")
                tfpackageData["locrel:prc.foaf:Person.foaf:title"] = creator.get("Honorific").toString()
                tfpackageData["locrel:prc.foaf:Person.foaf:givenName"] = creator.get("Given_Name").toString()
                tfpackageData["locrel:prc.foaf:Person.foaf:familyName"] = creator.get("Family_Name").toString()

        ###Processing 'coinvestigators' metadata
        coinvestigators = data.get("coinvestigators")
        for i in range(len(coinvestigators)):
            tfpackageData["dc:contributor.locrel:clb." + str(i + 1) + ".foaf:Agent"] = coinvestigators[i]

        ###Processing 'anzsrcFOR' metadata
        anzsrcFOR = data.get("anzsrcFOR")
        for i in range(len(anzsrcFOR)):
            anzsrc = anzsrcFOR[i]
            #Querying against The Mint, but only using the first 4 numbers from anzsrc, this ensure a result
            sock = urllib.urlopen(theMintHost + "/ANZSRC_FOR/opensearch/lookup?count=999&level=http://purl.org/asc/1297.0/2008/for/" + anzsrc[:4])
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
                        tfpackageData["dc:subject.anzsrc:for." + str(i + 1) + ".skos:prefLabel"] = result.get("skos:prefLabel")
                        tfpackageData["dc:subject.anzsrc:for." + str(i + 1) + ".rdf:resource"] = rdfAbout

        ###Processing 'anzsrcSEO' metadata                        
        anzsrcSEO = data.get("anzsrcSEO")
        for i in range(len(anzsrcSEO)):
            anzsrc = anzsrcSEO[i]
            #Querying against The Mint, but only using the first 4 numbers from anzsrc, this ensure a result
            sock = urllib.urlopen(theMintHost + "/ANZSRC_SEO/opensearch/lookup?count=999&level=http://purl.org/asc/1297.0/2008/seo/" + anzsrc[:4])
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
                        tfpackageData["dc:subject.anzsrc:seo." + str(i + 1) + ".skos:prefLabel"] = result.get("skos:prefLabel")
                        tfpackageData["dc:subject.anzsrc:seo." + str(i + 1) + ".rdf:resource"] = rdfAbout

        ###Processing 'keyword' metadata                        
        keyword = data.get("keyword")
        self.utils.add(self.index, "keywords", keyword.toString())
        for i in range(len(keyword)):
            tfpackageData["dc:subject.vivo:keyword." + str(i + 1) + ".rdf:PlainLiteral"] = keyword[i]

        tfpackageData["dc:accessRights.skos:prefLabel"] = data.get("accessRights")
        tfpackageData["dc:license.dc:identifier"] = data.get("license").get("url")
        tfpackageData["dc:license.skos:prefLabel"] = data.get("license").get("label")

        #identifier
        tfpackageData["dc:identifier.redbox:origin"] = "external"
        tfpackageData["dc:identifier.rdf:PlainLiteral"] = recordIdentifier
        tfpackageData["dc:identifier.dc:type.rdf:PlainLiteral"] = "uri"
        tfpackageData["dc:identifier.dc:type.skos:prefLabel"] = "Uniform Resource Identifier"

        dataLocation = data.get("dataLocation")
        dataLocation = dataLocation.replace("%NAME_OF_FOLDER%", species)
        tfpackageData["bibo:Website.1.dc:identifier"] = dataLocation

        #The following have been intentionally set to blank. No mapping is required for these fields.
        tfpackageData["redbox:retentionPeriod"] = data.get("retentionPeriod")
        tfpackageData["dc:extent"] = "unknown"
        tfpackageData["redbox:disposalDate"] = ""
        tfpackageData["locrel:own.foaf:Agent.1.foaf:name"] = ""
        tfpackageData["locrel:dtm.foaf:Agent.foaf:name"] = ""

        ###Processing 'organizationalGroup' metadata
        organisationalGroup = data.get("organizationalGroup")
        for i in range(len(organisationalGroup)):
            organisation = organisationalGroup[i]
            #Querying against The Mint
            sock = urllib.urlopen(theMintHost + "/Parties_Groups/opensearch/lookup?count=9999&searchTerms=ID:" + organisation)
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
                tfpackageData["foaf:Organization.dc:identifier"] = orgGroup.get("dc_identifier")[0]
                tfpackageData["foaf:Organization.skos:prefLabel"] = orgGroup.get("Name")[0]

        tfpackageData["swrc:ResearchProject.dc:title"] = ""
        tfpackageData["locrel:dpt.foaf:Person.foaf:name"] = ""
        tfpackageData["dc:SizeOrDuration"] = ""
        tfpackageData["dc:Policy"] = ""

        self.__updateMetadataPayload(tfpackageData)
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

        try:
            wfMeta = self.__getJsonPayload("workflow.metadata")
            wfMeta.getJsonObject().put("pageTitle", pageTitle)

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

        # Has the workflow metadata changed?
        if wfChanged == True:
            inStream = IOUtils.toInputStream(wfMeta.toString(True), "UTF-8")
            try:
                StorageUtils.createOrUpdatePayload(self.object, "workflow.metadata", inStream)
            except StorageException:        
                print(" ERROR updating dataset payload")

        # Form processing
        coreFields = ["title", "description", "manifest", "metaList", "relationships", "responses"]
        formData = wfMeta.getObject(["formData"])
        if formData is not None:
            formData = JsonSimple(formData)
            # Core fields
            description = formData.getStringList(["description"])
            if description:
                self.descriptionList = description
            # Non-core fields
            data = formData.getJsonObject()
            for field in data.keySet():
                if field not in coreFields:
                    self.customFields[field] = formData.getStringList([field])

        # Manifest processing (formData not present in wfMeta)
        manifest = self.__getJsonPayload(self.packagePid)
        formTitles = manifest.getStringList(["title"])
        if formTitles:
            for formTitle in formTitles:
                if self.title is None:
                    self.title = formTitle
        self.descriptionList = [manifest.getString("", ["description"])]
        formData = manifest.getJsonObject()
        for field in formData.keySet():
            if field not in coreFields:
                value = formData.get(field)
                if value is not None and value.strip() != "":
                    self.utils.add(self.index, field, value)
                    # We want to sort by date of creation, so it
                    # needs to be indexed as a date (ie. 'date_*')
                    if field == "dc:created":
                        parsedTime = time.strptime(value, "%Y-%m-%d")   
                        solrTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", parsedTime)
                        self.utils.add(self.index, "date_created", solrTime)
                    # try to extract some common fields for faceting
                    if field.startswith("dc:") and \
                            not (field.endswith(".dc:identifier.rdf:PlainLiteral") \
                              or field.endswith(".dc:identifier") \
                              or field.endswith(".rdf:resource")):
                        # index dublin core fields for faceting
                        basicField = field.replace("dc:", "dc_")
                        dot = field.find(".")
                        if dot > 0:
                            facetField = basicField[:dot]
                        else:
                            facetField = basicField
                        #print "Indexing DC field '%s':'%s'" % (field, facetField)
                        if facetField == "dc_title":
                            if self.title is None:
                                self.title = value
                        elif facetField == "dc_type":
                            if self.dcType is None:
                                self.dcType = value
                        elif facetField == "dc_creator":
                            if basicField.endswith("foaf_name"):
                                self.utils.add(self.index, "dc_creator", value)
                        else:
                            self.utils.add(self.index, facetField, value)
                        # index keywords for lookup
                        if field.startswith("dc:subject.vivo:keyword."):
                            self.utils.add(self.index, "keywords", value)

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
            package = JsonSimple(JsonObject(data))
            # Store it
            inStream = IOUtils.toInputStream(package.toString(True), "UTF-8")
            try:
                self.object.createStoredPayload("formData.tfpackage", inStream)
                self.packagePid = "formData.tfpackage"
            except StorageException, e:
                self.log.error("Error creating 'formData.tfpackage' payload for object '{}'", self.oid, e)
                raise Exception("Error creating package payload: ", e)

    def __updateMetadataPayload(self, data):
        # Get and parse
        payload = self.object.getPayload("formData.tfpackage")
        json = JsonSimple(payload.open())
        payload.close()

        # Basic test for a mandatory field
        title = json.getString(None, ["dc:title"])
        if title is not None:
            # We've done this before
            return

        # Merge
        json.getJsonObject().putAll(data)

        # Store it
        inStream = IOUtils.toInputStream(json.toString(True), "UTF-8")
        try:
            self.object.updatePayload("formData.tfpackage", inStream)
        except StorageException, e:
            self.log.error("Error updating 'formData.tfpackage' payload for object '{}'", self.oid, e)