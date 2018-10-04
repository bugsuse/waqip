### WAQIP 

The waqip program is to download air quality data in China and save to mysql database from [aqicn.org](http://aqicn.org). 



This program include four python scripts as follows:

* aqi.py  :  to caculate IAQI(Individual Air Quality Index) and AQI(Air Quality Index) based on pm2.5, pm10, co, no2, so2, o3, and caculate the value of individual elements (such as pm2.5, pm10) based on IAQI for each elements.
* waqip.py : to download air quality index including AQI, IAQI for each elements (such as pm2.5, pm10, co, no2, so2, o3) and atmosphere data including temperature, pressure, humidity and wind.
* get_cities_china.py : to get the all of urls of air quality station in China
* get_waqip_all.py : to download air quality data and save to database. 

(**Note**: In order to successfully download data, you must be to get a token from [aqicn.org](http://aqicn.org))


The bash shell script waqip.sh is used to set crontab task, cities_china_url.csv include the informations of all of stations in China. 



Please put forward issue if you have any questions.


### WAQIP (中文)

waqip项目是为了从[aqicn.org](http://aqicn.org)网站下载中国各国控站的空气质量数据以及气象数据，并且存储到数据库。



其中包括了四个主要脚本：

* aqi.py : 可以根据pm2.5, pm10, co, no2, so2, o3的值计算IAQI和AQI，也可以根据各个要素的分指数计算各要素的值。
* waqip.py : 下载空气质量数据(包括各要素的分指数以及AQI)以及气象数据(包括温度，气压，湿度和风速等数据)。
* get_cities_china.py : 获取中国所有国控站的链接。
* get_waqip_all.py : 下载数据并存储到数据库。

(**注意**:为了能够成功下载数据，必须要从[aqicn.org](http://aqicn.org)网站申请token。)



waqip.sh 脚本可用于设置 crontab 定时任务，而 cities_china_url.csv 文件中包含了中国所有国控站的信息。



如果你有任何问题，欢迎提issue。

