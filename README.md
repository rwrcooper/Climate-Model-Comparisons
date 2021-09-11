# multi-model-analyses

Self contained example of climate model downloader, pre-processor and multi-
model analyses.

There is no interface here, all files are bash executable. I am unable to
provide an interface.

All files include brief instructions for use.

These files are used to analyse how the climate risk hazards of:

- extreme heat
- extreme wind
- fire weather
- drought
- flood

behave in different downscaled climate models. The rcp85 scenario is used for
for all models and models are compared through timeseries plots for selected cities, heatmaps and
spatial slope plots for the whole domain(a linear model is calculated for each grid-cell and the
value of the slope for each grid-cell is presented on the plot using colours).


## Example results

The analysis was done for all available models for the domains: Africa, Australia, Central America, East Asia, Europe, North America, South America, and for all hazards listed above.

Here is a short summary of results. We will look at the *East Asia* domain (EAS-44) (as there were only 4 model available, some other domains had up to 22) and the hazard *extreme heat* (tasmax).

### Slope plots

For the slope plot a linear model was produced for each grid cell for the values of annual maximum temperature from years 2000 to 2100. The slope (trend) for each grid-cell is shown for each available model. The same colour scheme is used for each model for comparrison. This is displayed next to a time-mean of the metric for each gridcell over the years 1981 to 2010.

![tasmax_yearmax_slope](https://user-images.githubusercontent.com/48542067/132932534-7c76211c-7b65-490a-a8d5-e5eb063782e7.png)

### Timeseries plots

![tasmax_yearmax_timeseries](https://user-images.githubusercontent.com/48542067/132932548-0ea96b42-22c6-4e73-9f65-78ebf55b2d8d.png)

### Heatmaps and table of values

![EAS-44_tasmax_yearmax_slopes_heatmap](https://user-images.githubusercontent.com/48542067/132933182-d1bc45d1-9ce3-44c3-9797-65372326efb8.png)

