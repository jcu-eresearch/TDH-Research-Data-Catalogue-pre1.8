Adding a new Research Data Record
=================================

To add a new research record to Research Data, you need to access the Dashboard. You can 
access the Dashboard from the home page by clicking on Dashboard in the menu bar or be 
going directly to http://research.jcu.edu.au/researchdata/dashboard. If you are not already
logged into the site, the login box will appear at this point.


Logging In
----------

.. figure:: _static/Login-Dialog.png 
   :width: 100%
   :figwidth: 50%
   :figclass: float-right
   
   Click on the orange AAF logo to log in to the site

JCU staff and students can authenticate to the site via the Australian Access Federation 
login.

.. raw:: html

   <div style="clear: both" ></div>

.. figure:: _static/AAF-Select-Institution.png
   :width: 100%
   :figwidth: 50%
   :figclass: float-right

   Pick your institution from the list. You can check the second tick box to remember this 
   setting from now on.

You will need to specify James Cook University as your institution

.. raw:: html
   
   <div style="clear: both" ></div>

.. figure:: _static/JCU-CAS-login.png
   :width: 100%
   :figwidth: 50%
   :figclass: float-right

   Log in with your normal JCU username and password

Then authenticate at the normal JCU login page. Once you have logged in you will be 
returned to the dashboard.

.. raw:: html
   
   <div style="clear: both" ></div>

Creating a new JCU Research Record
----------------------------------

The Researcher Dashboard provides you with the facility to create a research record. A research 
record contains information about your research data:

* Who collected the data
* Why it was collected
* Where and when it was collected
* What publications or other research outputs are related to your data
* How your data can be accessed and how it should be cited.

To create a new research record, click on “Add a new JCU Research Record”.

.. figure:: _static/researcher-dashboard.png
   :width: 100%
   :figwidth: 100%


The web form for a new research record consists of 8 tabs. You can save and close
the form at any stage provided you have completed the required fields on the
open tab. Require fields are marked by an asterisk (*). For example, the
Content tab shown above has Title, Descriptions, and Collection Type as
required fields. Provide these have some data in them, you could save the form
at this point without completing any of the other tabs.

.. figure:: _static/New-dataset-form.png
   :width: 100%
   :figwidth: 100%

Help for each field can be viewed by clicking on the orange question mark |help-icon|.

.. |help-icon| image:: _static/Help-icon.png

The Content tab
---------------

This section of the form contains three fields - all of which are required:

Title
`````

Remember, the title will be what appears in any citation of your dataset - 
`Fred's Dataset` is not ideal.
Titles should be as descriptive as possible. They should include keywords to
provide context for non-specialist users, as well as information such as the
nature of the data and spatial and temporal coverage.  For example, a
collection named "Pilbara" may be adequate in the context of a particular
discipline database, but not in a repository that contains multiple discipline
outputs.  It would be more informative to provide a name like `Western
Australian Geological Survey: Pilbara` or `Aboriginal Art Collection: Pilbara,
1950-1965`.  Research record titles should be unique and generally should not use
acronyms. 

Descriptions
````````````

Ideally, you should provide at least two descriptions: a `brief` description and a `full` description. Select the type of description you are adding from the **Type** drop down and provide the text in the **Description** box. To add another description, use the **Add description** button. Once more than one description is present, a **Remove** buttion appears at the end of each description allowing you to delete an entry.

Possible description types are:

**Brief**
  The brief description should be one or two sentences that describe the dataset in a manner understandable to the lay-person.
**Full**
  Include a description of the kind of data in the dataset, how it was
  collected or analysed as well as describing what the dataset is about.
  Remember describe the *dataset* not the overall project or the publication.
**Note**
  The note type can be used to include additional information such as 

  * the size of the data download,
  * the different file formats used in the dataset
  * acknowledgements of funding bodies

**Logo**
   If your dataset is associated with a project or organisation with a logo
   that you would like displayed  on the dataset's page when it is displayed in
   Research Data Australia, you can include the url to the logo in this type.

.. figure:: _static/Description-widget.png
   :width: 100%
   :figwidth: 100%

Collection Type
```````````````

Research data collections can be classified as a

* Catalogue or Index
* Collection
* Registry
* Repository
* Dataset

.. figure:: _static/cpgdectree.png
   :width: 100%
   :figwidth: 100%

   Decision tree to help determine the type of Research data collection you have.
   Image curtesy of Australian National Data Service (http://ands.org.au).


Coverage
--------
The Coverage tab contains metadata that specifies the time span and location relevant to your data.

Date Coverage
`````````````
The date coverage allows you to specify the time period relevant to your date - to could be a start and end date for the data collection or it could be a time period such as *World War II* or *The Dark Ages*. For example, if your research data relates to samples you have collected and analysed (e.g. temperature readings, soil pH, blood tests, biological samples) then the date coverage would be:

* start of data collection - 1st of October 2011 e.g. 2011-10-01
* end of data analysis - 30th of November 2013 e.g. 2013-11-30

In this case you would use the date picker widgets to enter in these exact dates in the **From:** and **To:** fields and you would leave the **Time Period** text field empty.

.. figure:: _static/coverage-dates.png
   :width: 100%
   :figwidth: 50%
   :align: center

   When exact dates are relevant to the research dataset being describe, use the From and To fields.

If your research was an analysis of the 1920s fashion then, rather than the dates you collected your material, the relevant time period would be "The 1920s" and you would leave the **From:** and **To:** fields empty and enter "The 1920s" into the **Time Period** field.

.. figure:: _static/coverage-text.png
   :width: 100%
   :figwidth: 50%
   :align: center

   When a phrase describing the time period being consider is more appropriate then exact dates, use the Time Period field.

So - use either the **From:** and **To:** fields *or* the **Time Period** field but not both!

Hints
~~~~~

1. You can type your date into the **From:** and **To:** fields rather than
   using the date picker widget if you prefer. Just ensure you use the
   YYYY-MM-DD or YYYY format.  
2. Not all research data collections have a
   start and an end date. It may be that the research is ongoing and so you
   only have a start date. In this case, leave the **To:** field empty.

Geospatial Location
````````````````````

The Geospatial location is used to describe the region on Earth that is
relevant to the research data. This is not a required field as not all datasets
have a geospatial location. If this field is relevent to your research, there are three formats for adding geospatial data:

1. Provide a text description of the location - e.g. *30km SW of Port Douglas, Queensland, Australia*. 
2. Provide the ISO 3166-1 code for a country (http://www.iso.org/iso/home/standards/country_codes/iso-3166-1_decoding_table.htm).
3. Use the map widget to locate the area of interest and use the drawing tools to show the locations. 

Multiple geospatial locations can be provided for a single research record and any of the above methods can be used.


Adding a text description of country code can be acheived by using the Location Type and Value field - these can be seen below the map widget.




Using the map widget
~~~~~~~~~~~~~~~~~~

The table below explains the different tools available in the map and how to use them.

+--------------+---------------------+-------------------------------------------+
| Icon         |  Action             | Explaination                              |
+==============+=====================+===========================================+
| |drag|       | Drag map            | Click and hold the left mouse             |
|              |                     | button key to drag the map.               |
|              |                     | You can also click and hold               |
|              |                     | the right mouse button to select          |
|              |                     | an area and the map will zoom and         |
|              |                     | centre the map over the selected area.    |
+--------------+---------------------+-------------------------------------------+
| |point|      | Add a point         | Click on the map with the left mouse      |
|              |                     | button to add a point.                    |
+--------------+---------------------+-------------------------------------------+
| |bbox|       | Add an area using a | Click and hold the left mouse and         |
|              | bounding box        | drag to the size wanted. Release the      |
|              |                     | mouse button to finish the box.           |
+--------------+---------------------+-------------------------------------------+
| |polygon|    | Add a polygon       | Click the left mouse to start the         |
|              |                     | shape. Click as many points as needed     |
|              |                     | and double click on the last point to     |
|              |                     | close the shape.                          |
+--------------+---------------------+-------------------------------------------+
| |linestring| | Add an open shape   | Click the left mouse to start the         |
|              |                     | shape. Click as many points as needed     |
|              |                     | and double click on the last point        |
|              |                     | finish the shape.                         |
+--------------+---------------------+-------------------------------------------+
| |circle|     | Draw a circle       | Click (on the location you want to        |
|              |                     | have as the centr of the circle) and      |
|              |                     | hold the left mouse button and drag to    |
|              |                     | the desired size. Release the mouse button|
+--------------+---------------------+-------------------------------------------+
| |edit|       | Edit the map        | Click on/inside the shape you want to     |
|              |                     | edit - it will turn blue. To move the     |
|              |                     | shape as a whole click and hold on the    |
|              |                     | centre point for the shape and drag to    |
|              |                     | the desired location. To move a single    |
|              |                     | vertice, click and drag it to the new     |
|              |                     | location.                                 |
+--------------+---------------------+-------------------------------------------+


.. |drag| image:: _static/map-drag.png
.. |point| image:: _static/map-point.png
.. |bbox| image:: _static/map-bounding-box.png
.. |polygon| image:: _static/map-polygon.png
.. |linestring| image:: _static/map-linestring.png
.. |circle| image:: _static/map-circle.png
.. |edit| image:: _static/map-edit.png

As you add items to the map, 

.. note:: There is currently a bug in the *Edit the map* feature. When you edit a shape it will create new line
