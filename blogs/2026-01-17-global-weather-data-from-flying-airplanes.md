---
title: "Global weather data from flying airplanes"
date: "2025-11-03T15:38:03.939Z"
author: "Alexey Milovidov"
category: "Engineering"
excerpt: "Is it possible to derive global weather data from airplanes telemetry?"
---

# Global weather data from flying airplanes

Recently, I read the blog post by [Niklas Oberhuber](https://obrhubr.org/adsb-weather-model) showing that it is possible to derive weather data from airplane telemetry. Airplanes don't broadcast temperature or wind data, but it can be calculated on the fly from other parameters. I immediately decided to reproduce these calculations to show something beautiful!

[ADS-B Massive Visualizer](https://adsb.exposed/) collects telemetry from airplanes, such as their position, altitude, speed, and heading. This data is saved in the ClickHouse database. The service provides access to custom reports on top of over 150 billion data points and counting, accumulating them in real time.

You can read more about the service in the previous [blog post](https://clickhouse.com/blog/interactive-visualization-analytics-adsb-flight-data-with-clickhouse).

![title2.png](https://clickhouse.com/uploads/title2_f2f62c67b6.png)

## Sensors

Aircraft have many air pressure sensors, named "pitot tubes", which measure how the aircraft moves through the air. Static air pressure will show the altitude, and dynamic air pressure will show the airspeed relative to the air. These pressure sensors are the most important for flying dynamics.

Aircraft also have various navigation systems, which can show the altitude, speed, and heading, relative to the Earth. These measurements are less important to how the aircraft flies, but more important to navigation.

If we compare the values of these measurements to each other, we can derive more data. For example, comparing the airspeed with geometric speed will show us the speed of the tailwind (or headwind). Comparing the altitude from the pressure sensors with the geometric altitude could give some information about the local pressure changes and, maybe, temperature. Finally, comparing the heading relative to the air with the geometric heading will give us information about the wind direction.

## Visualizations

Let's suppose we want to visualize the angle (0..360 degrees) on the map. How to do it? We can use the color circle! So, different angles will be shown as different hues of color. For this purpose, ClickHouse provides functions for [conversions between color spaces](https://presentations.clickhouse.com/2025-release-25.7/#9): `colorOKLCHToSRGB` and `colorSRGBToOKLCH`.

The color space that most of the displays and graphic cards use is named sRGB, and contains three channels (Red, Green, and Blue) that are Gamma-corrected (they are non-linear to provide more resolution to darker colors, as they are easier to distinguish relatively to each other than the brighter colors).

There is another color space, named [OKLCH](https://oklch.com/). It contains three channels: Lightness, Chroma, and Hue. It is cylindrical, because the L and C channels range in the line (say, between 0 and 1; however, some of the values can be out of range of the display device), and the Hue channel is circular (represents an angle between 0 and 360). It is designed to be linear (which means, if we do a linear gradient in that color space, the gradient will look okay, hence the name) and intended to be perceptually uniform (which means, if you average between two colors in that space, the resulting color is also perceived as the average; if you fix the Lightness and Chroma and change the Hue, the result will be perceived as having the same brightness).

Let's map aircraft headings using this color space:

[![heading.png](https://clickhouse.com/uploads/heading_87061b8bfa.png)](https://adsb.exposed/?dataset=Planes&zoom=5&lat=36.0314&lng=-98.4165&query=ed99deb24cc4f2a2026034df3d7dd447)

## Pressure

Let's filter data for airplanes at least at 10,000 feet and map the difference between the `altitude` and `geometric_altitude` for a certain day:

[![pressure.png](https://clickhouse.com/uploads/pressure_4c97106659.png)](https://adsb.exposed/?dataset=Planes&zoom=5&lat=37.1785&lng=-95.2295&query=d095cd7b312291b682d3c9f1dafad188)

This looks surprisingly beautiful! Even more interesting, the picture changes if you select a different day.

<div style="height: 500px;"><video style="height: 100%;" src="https://clickhouse.com/uploads/pressure_cb1ce8d22f.mp4" autoplay loop muted playsinline></video></div>
<small style="color: gray;">Visualization of the air pressure difference across the US during 25 days starting from Apr 2, 2025. Each frame represents a 24-hour sliding window, and frames advance by 6 hours.</small>

I didn't derive the actual temperature from this data. The formula from Wikipedia looks complex, and I didn't want to apply it. Niklas Oberhuber also didn't use the formula but created a model instead. And I was just satisfied with nice pictures.

## Crabbing angle

When there is a strong but consistent crosswind, airplanes fly pointed into the wind. They can even land while pointed into the wind, which is called "crabbing". In the ADS-B data, there are two fields: one is `track_degrees`, which means the angle the plane points to, and another is `aircraft_true_heading`, which means the angle relative to the moving air around the airplane. If we subtract one angle from another, we will get the "crabbing" angle. Let's visualize it:

[![crabbing.png](https://clickhouse.com/uploads/crabbing_319dc835ee.png)](https://adsb.exposed/?dataset=Planes&zoom=5&lat=45.4119&lng=4.8697&query=6b7872ee6c34260ef470f5fd675f7d58)

Unfortunately, most of the data is not available in the US, but it is available in the EU. Probably, it is due to some local regulations.

## Wind

Now let's calculate the wind direction and speed. It will require some trigonometry, and trying to understand these formulas is difficult without a pen and paper.

Here is the "crabbing angle" (or name it "drift angle") we calculated in the previous step:
```(sql)
positiveModulo(track_degrees - aircraft_true_heading + 180, 360) - 180 AS drift_angle,
```

The wind speed can be calculated in the following way: draw a triangle with the `ground_speed` as one side and the `aircraft_tas` (airspeed) as the other side, with the angle `drift_angle` between these two sides. The length of the other side (the difference between the vectors of `ground_speed` and `aircraft_tas`) is the wind speed:

```(sql)
sqrt(
    pow(ground_speed, 2) + pow(aircraft_tas, 2) -
    2 * ground_speed * aircraft_tas * cos(radians(drift_angle))
) AS wind_speed,
```

Use a similar rule to calculate the absolute wind direction angle:

```(sql)
positiveModulo(track_degrees +
    if(drift_angle < 0, -1, 1) * degrees(acos(
        greatest(-1, least(1,
            (pow(ground_speed, 2) + pow(wind_speed, 2) - pow(aircraft_tas, 2)) /
            (2 * ground_speed * if(wind_speed > 0.1, wind_speed, 1))
        ))
    )) + 180, 360
) AS wind_direction,
```

We would like to show the wind direction on the map. But sometimes one pixel on the map will contain multiple data points, and we need to aggregate them to calculate the average. How to calculate the average of angles, e.g., what is the average between 10 degrees and 350 degrees? (The answer should be zero.) Actually, we need even more: calculate the weighted average of wind direction angles with the wind speed as the weight, so the stronger wind will have a bigger contribution.

To do this, let's say that the wind direction and wind speed are polar coordinates of the wind vector. And what we need in the result is the average wind vector. The average is a function in the linear coordinate space, which is why we can't apply it simply in the polar coordinates. We can do a coordinate transform of the function, but put it more simply, we should convert our (direction, speed) coordinates to linear (x, y), then do the average across both x and y coordinates, then convert it back to the polar space and take the angle back as the average:

```(sql)
positiveModulo(degrees(atan2(
    avg(sin(radians(wind_direction)) * wind_speed),
    avg(cos(radians(wind_direction)) * wind_speed)
)), 360) AS avg_wind_direction,
```

Now, given the wind angle and wind speed, it will be natural to map the angle to the color hue and the speed to the color lightness:

[![wind.png](https://clickhouse.com/uploads/wind_edc9f29b7d.png)](https://adsb.exposed/?dataset=Planes&zoom=5&lat=45.4119&lng=4.8697&query=ec1376e91336d70a77914a6ea2c22acc)

I compared the resulting picture to the actual weather data at https://earth.nullschool.net/ and it looked exactly as expected!

<div style="height: 550px;"><video style="height: 100%;" src="https://clickhouse.com/uploads/wind_f6f91a5794.mp4" autoplay loop muted playsinline></video></div>
<small style="color: gray;">Visualization of the wind across Europe during 25 days starting from Jan 1, 2025. Each frame represents a 24-hour sliding window, and frames advance by 6 hours.</small>

## Bottom line

ADS-B is a treasure trove of data, and it really shines when it is queryable in real-time with ClickHouse.

<small style="color: gray;">Bonus: how to do video visualizations. Prepare a query [as follows](https://pastila.nl/?03f73efc/6e0a10a5586f9a049a6747c36feb7373#oCbctgncESvUFSUc8eteyg==). Copy it to adsb.exposed. Open the browser console. Copy and run the following snippet: `frame = 0; const id = setInterval(() => { query_elem.value = query_elem.value.replace(/(\d+) AS frame/, `${frame} AS frame`); updateMap(); if (frame >= 100) { clearInterval(id) }; ++frame; }, 10000)`. The first run is needed to bring the images to the cache. After it finishes, replace the update interval to one second, start `recordmydesktop` and repeat the run. The generated video can be processed with ffmpeg as follows: `ffmpeg -y -i out.ogv -ss 4.5 -to 105 -filter:v "crop=2149:1218:893:666,thumbnail=15,setpts=0.1*PTS" -qscale:v 10 -an pressure.ogv`, where the time offsets are found manually by looking at the video, and crop frame is determined by taking a screenshot and using the selection tool in the graphic editor. The ffmpeg invocation is constructed by Claude.</small>