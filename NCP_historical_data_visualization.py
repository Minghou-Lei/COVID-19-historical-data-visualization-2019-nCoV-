import pandas as pd
import datetime
from typing import List
import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Timeline, Grid, Bar, Map, Pie, Line

# 显示所有列(参数设置为None代表显示所有行，也可以自行设置数字)
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置数据的显示长度，默认为50
pd.set_option('max_colwidth', 200)
# 禁止自动换行(设置为False不自动换行，True反之)
pd.set_option('expand_frame_repr', False)

url = 'https://raw.githubusercontent.com/BlankerL/DXY-2019-nCoV-Data/master/csv/DXYArea.csv'
df = pd.read_table(url, sep=',')

provinceName = ["上海", "云南", "内蒙古", "北京", "吉林", "四川",
                "天津", "宁夏", "安徽", "山东", "山西", "广东",
                "广西", "新疆", "江苏", "江西", "河北", "河南",
                "浙江", "海南", "湖北", "湖南", "甘肃", "福建",
                "西藏", "贵州", "辽宁", "重庆", "陕西", "青海", "黑龙江"]

# 格式化DataFrame的日期
df.drop(['cityName', 'city_confirmedCount', 'city_suspectedCount',
         'city_curedCount', 'city_deadCount'], inplace=True, axis=1)
df['updateTime'] = pd.to_datetime(df['updateTime'])
df['updateTime'] = df['updateTime'].apply(
    lambda x: datetime.datetime.strftime(x, '%m-%d'))
df['provinceName'] = df['provinceName'].apply(
    lambda y: y[:3] if y == '内蒙古自治区' or y == '黑龙江省' else y[:2])

# 数据去重（一日内更新了多次的）
NCP_data = df.drop_duplicates(
    subset=['provinceName', 'updateTime'], keep='first', inplace=False)

print(df.shape)
print(NCP_data.shape)
# print(NCP_data)
# NCP_data.to_excel(excel_writer="tmp.xlsx",index=False,encoding='utf-8')

# 获取日期list
dateSeries = NCP_data.iloc[:, 5]
dateSeries.drop_duplicates(inplace=True)
date = dateSeries.to_list()

confirmed_date = {}
province_percent = {}
total_num = []

MapData = []
dict = {}
data = []
dict2 = {}
# list = []
tmpProvinceList = []
rdate = list(date)
rdate.reverse()

for i in date:
    # print(i)
    criteria = NCP_data['updateTime'] == i
    df = NCP_data[criteria]

    for index in df.index:
        tmpProvinceList.append(df.loc[index, 'provinceName'])
    qlist = list(set(provinceName) - (set(tmpProvinceList)))
    # 缺失省份的名单
    print(qlist)
    old_suspectedCount = 0
    old_curedCount = 0
    old_deadCount = 0
    old_confirmedCount = 0
    isChanged = False
    for q in qlist:
        for td in rdate[:rdate.index(i)]:
            criteria = NCP_data['updateTime'] == td
            tddf = NCP_data[criteria]
            for j in tddf.index:
                if str(tddf.loc[j, 'provinceName']) == q:
                    old_confirmedCount = int(tddf.loc[j, 'province_confirmedCount'])
                    old_curedCount = int(tddf.loc[j, 'province_curedCount'])
                    old_deadCount = int(tddf.loc[j, 'province_deadCount'])
                    old_suspectedCount = int(tddf.loc[j, 'province_suspectedCount'])
                    isChanged = True
                    break
        if isChanged:
            NCP_data = NCP_data.append({'provinceName': q,
                                        'province_suspectedCount': old_suspectedCount,
                                        'province_curedCount': old_curedCount,
                                        'province_deadCount': old_deadCount,
                                        'province_confirmedCount': old_confirmedCount,
                                        'updateTime': i
                                        }, ignore_index=True)
            isChanged = False

    tmpProvinceList.clear()

    all_cases = df['province_confirmedCount'].sum()
    confirmed_date[i] = all_cases
    total_num.append(all_cases / 100)
    total_num.sort()

NCP_data.reset_index(drop=True)

for i in date:
    criteria = NCP_data['updateTime'] == i
    df = NCP_data[criteria]
    df['percent'] = df['province_confirmedCount'] / confirmed_date[i]
    print(df.shape)
    for index in df.index:
        data.append({'name': df.loc[index, 'provinceName'], 'value': [int(
            df.loc[index, 'province_confirmedCount']), float(df.loc[index, 'percent']),
            str(df.loc[index, 'provinceName'])]})
    data = sorted(data, key=lambda x: -x['value'][1])
    MapData.append({'time': i, 'data': list(data)})
    data.clear()


# MapData = json.dumps(MapData, ensure_ascii=False)
# print(MapData)

def Reverse(lst):
    return [ele for ele in reversed(lst)]


time_list = Reverse(date)
# print(time_list)

fout = open('detail_content', 'w', encoding='utf8')
fout.write(str(MapData))
fout.close()

maxNum = 1200
minNum = 80


def get_year_chart(year: str):
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in MapData if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
        else:
            data_mark.append("")
        i = i + 1

    map_chart = (
        Map()
            .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" +
                      str(year) + "全国各省份NCP实时动态(数据来源:丁香园; 数据仓库:BlankerL/DXY-2019-nCoV-Data)",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        Line()
            .add_xaxis(time_list)
            .add_yaxis("", total_num)
            .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max")]),
        )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="全国各省份NCP实时动态(单位: 百人)", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
            .add_xaxis(xaxis_data=bar_x_data)
            .add_yaxis(
            series_name="",
            yaxis_data=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
            .reversal_axis()
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=40000, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
            .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.5)"
            ),
        )
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
            .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
            .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
            .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
            .add(map_chart, grid_opts=opts.GridOpts())
    )

    return grid_chart


if __name__ == '__main__':
    timeline = Timeline(
        init_opts=opts.InitOpts(
            width="1600px", height="900px", theme=ThemeType.DARK)
    )
    for y in time_list:
        g = get_year_chart(year=y)
        timeline.add(g, time_point=str(y))

    timeline.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=1200,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )

    timeline.render("NCP.html")
    print(MapData)
