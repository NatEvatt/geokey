---
layout: tutorial
title:  "Getting started — An overview of the platform"
---

Geographic data is usually collected and provided by local authorities. However, official information quite often does not reflect the situation the same way local residents perceive it. The concept of participatory mapping addresses this problem by providing local communities with tools and methods to collect, visualise and analyse geographic data to get a better understanding of the processes happening in their community and to support work to change places. 

[The platform] is a platform for participatory mapping. Consider it a data-centre for community-based mapping activities of different kinds. It provides a data base to store the data collected by your volunteers and the means to connect various front-end applications to collect data, visualise data and analyse data. If you want to run a mapping project tp map your neighbourhood, you can utilse the platforms adminstration panels to set up your project, define what data you want your peers to collect and define who will be able to contribute and access data. 

We agree, that this all sounds very technical, so let's have a look at this simple example: Let’s say, you want to create a map of your neighbourhood’s finest restaurants, pubs and local shops. Because you want to keep your maps tidy, only members of your communities that are trusted connoisseurs should be able to contribute data to your project. You also live in a small and trusted community, so not everyone should be able to read data from your project and, of course, you don’t want children to have access to information on local pubs. 

### Categories, data groupings and user groups — what is it all about?

Now, let’s see how this example translates in a project run with [the platform].

Community mapping ventures are organised into distinct projects. For each project you define a set of categories; in our case this would be one for each restaurants, pubs and local shops. Using categories you can define, which data you want your contributors to collect. For the category restaurants, this could be a name, its address, the number of available seats and cuisine being served at that place. These would be the fields of your category.

In order to allow a selected set of users to contribute data to your new project, you create a user group “Contributors” and grant its members permission to contribute. 

Now your contributors add data to the project, a few places for each category, but so far nobody can actually access your data. You provide access to your data using data groupings. Data groupings are assigned with a set of filters that define, which data will be accessible through that grouping. As you want to provide access to all of your data, but restrict access for children to local stores and restaurants only, you create three data grouping — one for each category.

Finally, you grant permissions to access these data groupings to your users. Your contributors are all adults, so you simply permit access to all three data groupings to that user groups. 

You also create two additional user groups: Community Members and Children. You grant both groups read-only permissions as you don’t want their members to contribute. The group Community Members will be granted access to all three data groupings whereas Children will be granted access to the data groupings restaurants and local shops. 

Now you should be all set up and ready to go.

### Now really… how can I contribute and view my data?

As we pointed out earlier, [the platform] is just the data hub for your maps data. There is a couple of third-party applications that were build on top of [the platform] that you can use for contributing and viewing data.

- [Mapping for Change](http://mappingforchange.org.uk/) has developed a sophisticated client called [Community Maps](http://communitymaps.org.uk), which you can use for free. 
- [EpiCollect](http://www.epicollect.net/) has a mobile application that connects to [the platform]. You can used it for data collection.

### Where next

<ul class="next-links tutorial-links">
    <li>
      <h6><a href="{{site.url}}help/how-to-create-project.html">Create your first project</a></h6>
      <p>Learn how to setup your first project.</p>
    </li>
    <li>
     <h6><a href="../developers/">Developers</a></h6>
      <p>Learn how to install [the platform] on your server or how to use the API to build apps.</p>
    </li>
</ul>