---
title: "Ten years of open source: a stained-glass view"
date: "2026-06-19T13:32:00.312Z"
category: "Company and culture"
excerpt: "ClickHouse has been open source for ten years. At Open House San Francisco, we explored this in greater detail in the day 2 keynote. We've all heard open source described as a cathedral and a bazaar, a big tent, etc.   We tried a different analogy: staine"
---

# Ten years of open source: a stained-glass view

ClickHouse has been open source for ten years. At Open House San Francisco, we explored this in greater detail in the day 2 keynote. The following is a longer form, written version of the presentation with key slides highlighted. \
 \
We've all heard open source described as a cathedral and a bazaar, a big tent, etc. 

 \
We tried a different analogy: stained glass. Not as decoration, but as a picture of how thousands of people working over the years become one thing the world actually runs, without flattening any of them into a single hero story.

![stained-glass-light-lead-pieces.jpg](https://clickhouse.com/uploads/stained_glass_light_lead_pieces_47c5c13085.jpg)

**TL;DR**

* Stained glass is a useful lens for ten years of open source: many pieces held by lead, light only matters when it passes through, and repair is how the thing survives long enough to matter.
* cBioPortal shows what that looks like in production: when queries run in seconds instead of minutes, researchers keep exploring.
* ClickHouse ships contributor credit in the product itself via <code>[system.contributors](https://clickhouse.com/docs/en/operations/system-tables/contributors)</code>, queryable with the same engine you use for your data.
* The community story and the product story are one aperture: git history, GitHub activity, and shipped acknowledgments, all readable in SQL.


## Light, lead, and many pieces

Coloured glass arrives cut to shape, each piece chosen for where it will sit. Metal channels hold the pieces without smearing them into each other. Stone holds the whole frame so light can pass through. From inside, the picture glows. From the street, you often see a dark lattice first, then colour at the edges.

A stained-glass window is not a painting you hang on a wall. It is an interface between outside and inside, and the picture only means something when light actually crosses it. Public datasets read the same way: the same facts look different depending on where you stand.

In the great Gothic churches of medieval Europe, the window was architecture of light. Theology and story lived in fragments for people who would never read Latin manuscripts. The window was the public interface: high enough to lift your eyes, bright enough to read in color. Guilds guarded recipes for ruby and blue. A rose window is not one ego. It is a commission that outlived any single pair of hands.

![gothic-rose-window.jpg](https://clickhouse.com/uploads/gothic_rose_window_7ab6f219d8.jpg)

The craft did not stay in the nave. It moved into palaces, town halls, and the industrial century. Tiffany treated glass like material science and factory choreography: iridescence from metal oxides, furnaces, teams of cutters selecting and foiling pieces. That is closer to how we build software than the cathedral is: recipes, tooling, taste, throughput, and still a window that has to read from a distance and survive weather.

![tiffany-industrial-stained-glass.jpg](https://clickhouse.com/uploads/tiffany_industrial_stained_glass_caae5c572f.jpg)

You know Notre Dame. In April 2019, the spire came down on live television. For a few hours, it looked like eight centuries might end in a single night. It did not. The restoration took five years, 340,000 donors, and craftspeople who had to relearn techniques that had not been needed in a generation. Notre Dame reopened in December 2024. The rose window was still there: new lead, old glass where the piece could stay. Repair is how the thing survives long enough to matter.

![notre-dame-restoration.jpg](https://clickhouse.com/uploads/notre_dame_restoration_4208081965.jpg)

## Mosaic, not mural

Those centuries are why three lines from the talk are not slogans for us:
* Mosaic, not mural: authorship stays granular, and your eye can still find the cut.
* A window, not wallpaper: depth and transmission, not a flat texture pretending there is no structure underneath.
* Many cuts, one aperture: many kinds of work, visible through one opening the world shares.

Without these, the geometry is just pretty. What follows is counts, time, and participation: the whole window, not a cropped hero shot.

## Light through a real window: cBioPortal

Memorial Sloan Kettering runs [cBioPortal](https://www.cbioportal.org/), an open platform for cancer genomics: mutations, cohorts, survival, treatment. It started at MSK in 2011 and spread to institutions worldwide. Hundreds of thousands of patient records. Billions of data points.

The bottleneck was never missing data. It was waiting on the database. On the old stack, a filter could take a minute or more, and researchers stopped exploring. The team moved heavy filtering into ClickHouse in SQL instead of pulling huge result sets into the application. The portal got about ten times faster on the paths that matter. When the engine is fast enough, people keep using it. That is what we mean by light through the window.

![cbioportal-study-view.png](https://clickhouse.com/uploads/cbioportal_study_view_91b18310bf.png)

We wrote about the MSK work in detail in [How Memorial Sloan Kettering Cancer Center is using ClickHouse to accelerate cancer research](https://clickhouse.com/blog/how-memorial-sloan-kettering-cancer-center-is-using-clickhouse-to-accelerate-cancer-research). The short version: this is a real product in medicine, not a chart of our git history.

The analytics had to be fast first: cohorts, filters, and counts that return quickly. Then you can add a chat layer on top without making every question a side project. Natural language does not replace SQL or cBioPortal's charts. It is another way in: ask in plain language, then check the result in the tool you trust. Schema, filters, and what is actually in the cohort still matter. The engine underneath already answers in seconds, not minutes.

![cbioportal-ask-the-data.png](https://clickhouse.com/uploads/cbioportal_ask_the_data_a1d89ccd82.png)

## ClickHouse reads ClickHouse

The stained glass was our lens. This section is our instrument: raw signals in git, activity in GitHub's public archive, and names that ship inside the binary. We query the window with the same tool the world runs.

The product story and the community story share one aperture.

### How the demo is built

Nothing here is a magic trick with a hidden spreadsheet behind it. Three data sources, one engine:

<table>
  <tr>
   <td><strong>Source</strong>
   </td>
   <td><strong>What it is</strong>
   </td>
   <td><strong>How it arrived</strong>
   </td>
  </tr>
  <tr>
   <td>Git history
   </td>
   <td>One row per commit from a bare clone of <code>ClickHouse/ClickHouse</code>
   </td>
   <td>Loaded into ClickHouse Cloud with <code>INSERT ... FORMAT JSONEachRow</code>
   </td>
  </tr>
  <tr>
   <td><a href="https://www.gharchive.org/">GH Archive</a>
   </td>
   <td>Public GitHub events for one repo, one month, hourly files
   </td>
   <td>Loaded into a <code>github_events</code> table
   </td>
  </tr>
  <tr>
   <td><code><a href="https://clickhouse.com/docs/en/operations/system-tables/contributors">system.contributors</a></code>
   </td>
   <td>Acknowledgement rows inside the build you are connected to
   </td>
   <td>Shipped with the product
   </td>
  </tr>
</table>


Same engine for all three beats. Two of them we loaded. One shipped with the binary.

### Distinct contributors over time

Each step on the cumulative curve is a first appearance: an author who crossed into the repository's history for the first time, and then time stacks them. The curve counts distinct hands since the beginning, not weekly throughput. Artisans contributing features, tweaking lead via docs and READMEs, shaping what we have created.

![distinct-contributors-cumulative.png](https://clickhouse.com/uploads/distinct_contributors_cumulative_f2237675f8.png)

### Motion in the public log

Same repository, different source. In April 2025 alone, about 11,000 public events on `ClickHouse/ClickHouse`. Comments lead, then pushes and pull requests, then reviews, then new issues. One repo, one month. Not all of GitHub. That is participation with a defined window in the caption.

![github-archive-events-april-2025.png](https://clickhouse.com/uploads/github_archive_events_april_2025_d2845fb9fd.png)

### One counter, high closure rates

GitHub uses one counter for both issues and pull requests. On 19 March 2026, that counter crossed 100,000 on `ClickHouse/ClickHouse`. That is the whole public ledger: bug reports, feature requests, proposed changes. Employees and outside contributors on the same staircase.

A high issue count is not a problem. It means people bring work to the door. What matters is what happens after they knock. At the time of the talk, 83% of issues were resolved (23,016 of 27,600) and 99% of pull requests were closed (70,362 of 71,284). That is the rate of a project that stays legible at speed.

![github-counter-closure-rates.png](https://clickhouse.com/uploads/github_counter_closure_rates_cdca89b0c3.png)

For context on scale: MySQL's combined counter sits around 120,000. LLVM is around 187,000 with roughly 70% of issues closed. PostgreSQL still does much of its life on a mailing list, which is a perfectly honourable bug tracker if you enjoy arguing with archives. We are on the same wall as those projects. We show the closure rates next to the screenshot because throughput without resolution is just noise.


## system.contributors

When you look under `system.*`, most tables describe the machine: parts, settings, housekeeping. <code>[system.contributors](https://clickhouse.com/docs/en/operations/system-tables/contributors)</code> tells you about people. Names as rows, not as a footer on a marketing page. It ships inside the same artefact as the engine, so when we ask "who built this?" we are not fetching a vibe from a CMS. We are querying material.

When ClickHouse was first open-sourced, Alexey Milovidov imagined a day when someone would walk into an interview, be asked, "Have you built anything I know?", and be able to answer, "Query ClickHouse for my name." That is why this table exists, and that is why we keep updating it. Credit ships in the product, readable with the same tool the world already runs.

On the build we showed at Open House San Francisco, the count was 2,632: 


```
SELECT count() FROM system.contributors

```

Each row is someone whose work passed through the paths that put code in the binary. The list is large and still finite, and that is why it lands with weight. It is the same kind of object you query for customers. We want you to feel legibility applied to labor here, not only to logs.

Nobody hand-curates this list for a keynote. It is carried forward from the project's own accounting, the long trail of patches and merges git already remembers, folded into a list that travels with each version. When a build is cut, that build's acknowledgement set is what lands on disk. Two laptops on the same version read the same rows. That is community as frozen credit bundled with the bits, not a private cloud only insiders see.

The table has seams. Not every influence on the code shows up the same way, and the schema favors what ships. We would rather show honest seams than pretend the glass was poured in one sheet.


### Finding new contributors between releases

A wall of names on a slide is inscrutable. SQL makes the diff readable. Export contributor lists from two versions, then subtract:


```
sudo docker run --rm clickhouse/clickhouse-server:26.5 clickhouse-local \
  --query "SELECT * FROM system.contributors ORDER BY name" \
  > contributors_26.5.txt

./clickhouse local --query "
  SELECT arrayStringConcat(groupArray(line), ', ')
  FROM file('contributors_26.5.txt', LineAsString)
  WHERE line NOT IN (SELECT * FROM file('contributors_25.5.txt', LineAsString))
  FORMAT TSVRaw
"

```

Or check whether your name is already there:


```
SELECT * FROM system.contributors WHERE name ILIKE '%You%'

```

Maybe you are next.


## Champions: clearer lead around work that is already public

The charts showed motion. The contributor table showed names that ship. The query pointed back to the people in the room.

Contributors drive ClickHouse. People show up as patches, as threads, as talks, as docs, as the person answering the hard question in Slack at midnight. None of that is a side quest to the binary. It is the story.

Some contributors become [Champions](https://clickhouse.com/community): recognized teachers, writers, and advocates. Champions are not a replacement for contributing. They are clearer lead around work that is already public. We are saying out loud: we see this teaching, and we can help it travel farther. The glass was already there. Champions is the frame that says which pieces catch the light, so the room can find them faster.

The program sits close to where the work already happens. Names appear only where the person has consented, because consent matters more than a dramatic reveal. If Champions fits you, [clickhouse.com/community](https://clickhouse.com/community) has the full programme: invitations to events, career visibility, community recognition, and swag on top of the everyday work in issues, chats, and pull requests.


## Ten years in, light still has to pass

ClickHouse is a community and a database you can query, held together as one stained-glass window: many cuts of work, held in frame by infrastructure, meaningful because the thing runs out there in the light.

If you have ever wondered whether open source credit is real or performative, run a query. The names are in the binary. The issues and pull requests are in the public log. The researchers at MSK are filtering cohorts in seconds. Repair is normal. Light still has to pass.
