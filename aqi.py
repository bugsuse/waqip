# coding : utf-8

"""
   计算空气质量指数
"""

import numpy as np
import pandas as pd


class AQI(object):
    """ 根据给定空气污染数据计算AQI
    """

    def __init__(self, data=None, columns=None, freq='1h', clean=True, o38=False, dropna=False, interp=False,
                 style=False):
        """ 初始化

        data (pandas.DataFrame) : 包含所有要素的数据
        columns (list) : 参与计算的要素
        freq  (str) : 控制计算每小时AQI还是日均AQI，可选值为: '1h', '24h'
        clean (bool) : 是否对数据进行预处理，默认进行预处理
        o38  (bool) :  仅在 freq = '1h' 时有效，即是否对O3求8小时滑动平均，默认为False
        interp (bool) : 是否对缺失值进行插值，默认不插值
        style  (bool) : 返回AQI等级类型，数字还是字符，默认返回字符
        """
        if data:
            if clean:
                self.edata = self.clean_data(data, columns=columns, freq=freq, o38=o38)
            else:
                self.edata = data

            self.style = style

            if dropna:
                self.edata = self.edata.dropna()
            if interp:
                self.edata = self.edata.interpolate()

    def get_stddata(self, var):
        """ 获取指定变量的标准数据

        参数：
            var (str) : 污染物名称，比如pm2_5, pm10, co

        返回：
            对应污染物的值范围 (list)
        """

        iaqi = np.array([0, 50, 100, 150, 200, 300, 400, 500])
        so2_24h = np.array([0, 50, 150, 475, 800, 1600, 2100, 2620])
        so2 = np.array([0, 150, 500, 650, 800, 1600, 2100, 2620])
        no2_24h = np.array([0, 40, 80, 180, 280, 565, 750, 940])
        no2 = np.array([0, 100, 200, 700, 1200, 2340, 3090, 3840])
        pm10 = np.array([0, 50, 150, 250, 350, 420, 500, 600])
        pm2_5 = np.array([0, 35, 75, 115, 150, 250, 350, 500])
        pm10_24h = np.array([0, 50, 150, 250, 350, 420, 500, 600])
        pm2_5_24h = np.array([0, 35, 75, 115, 150, 250, 350, 500])
        co_24h = np.array([0, 2, 4, 14, 24, 36, 48, 60])
        co = np.array([0, 5, 10, 35, 60, 90, 120, 150])
        o3 = np.array([0, 160, 200, 300, 400, 800, 1000, 1200])
        o3_8h = np.array([0, 100, 160, 215, 265, 800, 1000, 1200])

        try:
            return eval(var)
        except NameError:
            raise NameError('所获取的变量 {0} 不在常数库中。支持获取的变量为以下变量：\
                             iaqi, so2_24h, so2, no2_24h, no2, pm10_24h, pm2_5_24h, \
                             co, co_24h, o3, o3_8h.'.format(var))

    def calculate_iaqi(self, var, cp):
        """计算各污染项目空气质量分指数

        参数：
            var (str)  : 污染物名称，比如pm2_5, pm10, co等
            cp (float) : 对应污染物的值

        返回：
            对应污染物的分指数 (float)
        """

        var_std = self.get_stddata(var.lower())
        iaqi = self.get_stddata('iaqi')
        # check values 
        if cp > var_std[-1]:
            cp = var_std[-1]
        elif cp < var_std[0]:
            raise ValueError('{0} value {1} less than {2}, please check it!'.format(var, cp, var_std[0]))

        con = var_std < cp

        bpl, bph = var_std[con][-1], var_std[~con][0]
        iaqil, iaqih = iaqi[con][-1], iaqi[~con][0]

        return (iaqih - iaqil) / (bph - bpl) * (cp - bpl) + iaqil

    def reverse_iaqi(self, var, iaqiv):
        """根据要素aqi分量计算要素原始值

        参数:
        --------------
        var (str): 要素名称
        iaqiv (list): 要素aqi分量

        返回:
        --------------
        要素原始值
        """
        var_std = self.get_stddata(var.lower())
        iaqi = self.get_stddata('iaqi')
        # check values 
        if iaqiv > var_std[-1]:
            raise ValueError('{0} value {1} less than {2}, please check it!'.format(var, iaqiv, var_std[0]))

        con = var_std < iaqiv

        bpl, bph = var_std[con][-1], var_std[~con][0]
        iaqil, iaqih = iaqi[con][-1], iaqi[~con][0]

        return (iaqiv - iaqil) * (bph - bpl) / (iaqih - iaqil) + bpl

    def calculate_aqi(self, edata=None):
        """计算aqi

        参数：
            edata (pandas.DataFrame) : 保存各污染物数据。注意：污染物名称要符合相应格式

        返回：
            edata (pandas.DataFrame) : 包含aqi和首要污染物的结果
        """
        if edata is not None:
            self.edata = edata
            raise ValueError('Input data edata is NoneType!')
        if self.edata is not None:
            edata = self.edata

        columns = edata.columns

        edata['aqi'] = np.nan
        edata['首要污染物'] = ''
        enums = np.arange(edata.shape[0])

        for i in enums:
            h = []
            for col in columns:
                h.append(self.calculate_iaqi(col, edata[col][i]))
            edata.loc[edata.index[i], 'aqi'] = np.max(h)
            edata.loc[edata.index[i], '首要污染物'] = ','.join(columns[h == np.max(h)].values)
        edata['level'] = edata['aqi'].apply(lambda x: self.get_level(x)).values

        return edata

    def get_level(self, aqi):
        """ 获取给定AQI值所对应的污染级别
        aqi (float, int) : AQI值

        返回:
            数字级别或对应的字符级别，默认返回字符级别
        """

        levels = np.array([0, 50, 100, 150, 200, 300])
        ranks = np.array([1, 2, 3, 4, 5, 6])
        strranks = np.array(['优', '良', '轻度污染', '中度污染', '重度污染', '严重污染'])

        if self.style:
            return ranks[aqi > levels][-1]
        else:
            return strranks[aqi > levels][-1]

    def clean_data(self, data, columns=None, freq='1h', o38=False):
        """处理空气质量数据为符合计算aqi程序接受的格式

        参数：
            columns (list) :
            freq (str) :
            o38 (bool) :

        返回：
            处理后的各空气
        """

        data.columns = [col.lower() for col in data.columns]

        if freq == '1h':
            if columns is None:
                columns = ['so2', 'no2', 'o3', 'co', 'pm2_5', 'pm10']
                data = data[columns]
            else:
                data = data[columns]

            if o38:
                data['o3'] = self.fast_moving_average(data['o3'], 8)  # 使用8小时滑动平均作为o3值

            return data[columns]
        elif freq == '24h':
            if columns is None:
                columns = ['so2_24h', 'no2_24h', 'o3_8h', 'co_24h', 'pm2_5_24h', 'pm10_24h']
                data = data[columns]
            else:
                data = data[columns]

            if 'o3_8h' not in columns:
                raise ValueError('Please use o3_8h to replace o3 column name!')

            elements = pd.DataFrame(columns=columns)
            for col in columns:
                if col.lower() == 'o3_8h':
                    o3_8h = pd.DataFrame(self.fast_moving_average(data[col], 8), index=data.index, columns=[col])
                    elements[col] = o3_8h.resample('1d').max()
                else:
                    elements[col] = data[col].resample('1d').mean()

            return elements
        else:
            raise ValueError('No support {0}. freq must be 1h or 24h.'.format(freq))

    def fast_moving_average(self, x, N):
        """计算移动平均
        """
        return np.convolve(x, np.ones((N,)) / N)[(N - 1):]
