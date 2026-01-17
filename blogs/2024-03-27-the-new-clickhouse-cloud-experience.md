---
title: "The new ClickHouse Cloud experience"
date: "2024-03-27T15:10:59.876Z"
author: "Gareth Jones"
category: "Product"
excerpt: "We've reworked ClickHouse Cloud from the ground up. A new navigation system brings the important features and controls closer to the user, while the SQL console has been fully integrated to create a singular, seamless experience."
---

# The new ClickHouse Cloud experience



<p style="color:rgb(150,150,150); margin-bottom:8px;">tl;dr</p>

This week, we're releasing a major update to ClickHouse Cloud. Over the last nine months, we've worked hard to rethink, redesign, and reimplement the Cloud user experience, and we're excited to share these changes with you today.

<iframe width="764" height="430" src="https://www.youtube.com/embed/bXTel-9olJ8?rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br/>

<hr style="border-color:rgb(50,50,50)" />

<br />
The ClickHouse SQL console is integral to the way many Cloud users interact with their data. To reflect its importance, the SQL console is now fully integrated and prominently located at the top of the service navigation menu, allowing for easy access at all times. The SQL console itself has undergone a significant revamp, with the team working hard to eliminate countless UI and networking bugs and to enhance the user experience of common workflows. We've added information on running queries, and performance enhancements, and improved the capabilities of our AI-powered SQL generator. When using the SQL console, the main navigation can be easily collapsed, providing you with the entire screen to fully immerse yourself in your work. These changes combine to create an experience that feels responsive, snappy, and more intuitive.

<br />
<br />

<video width="100%" height="240" controls>
  <source src="/uploads/sql_console_video_339d0dc7d3.mp4" type="video/mp4">
</video>
<p style="color:rgb(150,150,150); margin-bottom:8px; margin-top: 4px; font-size: 12px; width:100%; text-align:center; font-style:italic;">Demo of the ClickHouse SQL console</p>

<br />

There is much more to this update than just the SQL console, though. We've concentrated a huge amount of effort on making the process of data ingestion much more approachable and streamlined. In the new Cloud experience, Data Sources are located right below the SQL console in the navigation, again reflecting how central they are to the ClickHouse experience. Uploading a file now supports seven different popular file types and, along with importing from a URL, has been reduced to a sleek two-step, single-page task. Another area that really shines in the new UI is the simple step-by-step workflows for ingesting and managing streaming data in ClickHouse. We call these [ClickPipes](https://clickhouse.com/cloud/clickpipes), and we believe that the ease with which continuous data can be imported into ClickHouse Cloud will prove to be a game-changer.

<video width="100%" height="240" controls>
  <source src="/uploads/data_loading_video_a68add2b17.mp4" type="video/mp4">
</video>
<p style="color:rgb(150,150,150); margin-bottom:8px; margin-top: 4px; font-size: 12px; width:100%; text-align:center; font-style:italic;">Data ingestion in ClickHouse Cloud</p>
<br />

Performing common operational actions such as starting and stopping your service, adjusting autoscaling settings, or creating traffic filtering rules have been combined into a new Settings area, again, accessible from the main navigation. This gives you one single place to go and manage your infrastructure. If you have multiple services, there's a handy shortcut for switching between them in the navigation sidebar.

Outside of service-specific actions, there are Account and Organization-level controls that we've ensured are still just a click away. Items such as User Management, API Keys, and Billing, are all neatly located in the new Organization menu, while your Account profile and Security settings can be accessed from the menu triggered by the user avatar.

Providing both light and dark themes has become essential in modern web app development, and if you ask ten people which they prefer, there's a good chance you'll end up with an even split. For this reason, we felt it was important to give ClickHouse Cloud users the choice of how they want to experience the app.

<video width="100%" height="240" controls>
  <source src="/uploads/color_theme_video_1e29681ae0.mp4" type="video/mp4">
</video>
<p style="color:rgb(150,150,150); margin-bottom:8px; margin-top: 4px; font-size: 12px; width:100%; text-align:center; font-style:italic;">Dark and Light themes available in ClickHouse Cloud</p>
<br />

Building off our new design system and component library, [Click UI](https://click-ui.vercel.app), we've been able to create a modern, elegant, and consistent aesthetic throughout the Cloud experience. We firmly believe that in addition to being attractive and usable, the leading UI's are predictable. We felt that the best way to achieve that predictability was to implement and maintain a strict design system and consistent UX patterns.

While this was a lot of upfront work, it now allows us to design and develop at a rapid pace while staying on-brand and uniform in everything we do. This becomes ever-more important as teams grow and so it was important to establish this early in the ClickHouse company journey.

This is just the start, we have even more big improvements right around the corner. We'd love to hear your thoughts, so join our [slack channel](https://clickhouse.com/slack) if you have feedback or would like to follow along in our journey.

There's lots more I could say about the new, improved Cloud user experience, but why not take it for a spin yourself?
