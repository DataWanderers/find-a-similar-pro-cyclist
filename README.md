## What?
A tiny [app](nothing-here-yet) to find similar cyclists to chosen rider. The selection can be filtered based on age and country of origin.

## Why?
This little tool has several applications:
- Gaming (e.g. Pro Cycling Manager or Wielermanager)
- It can be used for transfers (to replace a certain rider), or for scouting (to find the next talent within a certain region)
- You can simply use it out of curiosity

There are of course much more advanced tools to use for above purposes, but it can provide quick and initial guidance.

## How?

### Data
The data come from the final community-made WorldDB 2021 database for the game Pro Cycling Manager (PCM) 2020. It can be downloaded from the Steam Workshop. Other databases (and for other PCM versions), with stats that would be equally interesting, can be found when you register to [pcmdaily.com](https://pcmdaily.com/). 

In the database, each rider has 13 characteristics representing various facets of cycling (such as climbing, sprinting, cobblestones, and so on). These stats have been extracted to Excel using this [tool](https://pcmdaily.com/infusions/pro_download_panel/download.php?did=1108), and are the sole basis for comparing riders.

Note that as the database is an update from 2021, it is not the most recent reflection of rider's capabilities (as an example, Tour de France 2022 winner Jonas Vingegaard is not at all the best climber). The cyclist's statistics are overall a very good representation nonetheless.

### Analysis

The tool is a Python Dash app. It is my first, and I just started with the official [tutorial](https://dash.plotly.com/installation), and then modified to my desired outcome. My development environment was PyCharm.

It is made available using a free Heroku server.

Not going to lie, the app **is** pretty ugly. I didn't bother to make it look nicer. Functionality first! To make it prettier, [this](https://dash-bootstrap-components.opensource.faculty.ai) would be a good resource I think.

The most similar riders are computed using the [FAISS library](https://github.com/facebookresearch/faiss). I based myself on the first example in [here](https://www.pinecone.io/learn/faiss-tutorial/). The library is much more powerful than what I use of it, but this use case didn't need more complexity. There are only 5000+ riders in the database, so I could use the exact L2 norm functionality. It compares the vector of the 13 characteristics for the chosen rider with the vectors for all riders, and returns those that have the smallest Euclidean distance (thus, are most similar).
