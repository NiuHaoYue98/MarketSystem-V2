# MarketSystem-V2
## 运行说明
运行Driver即可运行系统，Statistics.py是市场统计模块，在模拟实验结束之后进行市场统计
### Driver
控制模拟市场运行
* agent_flag = False    # 控制普通程式化交易者的信息输出，默认为Fasle
* list_flag = True      # 控制每轮交易的订单簿输出，默认为Flase
* high_flag = True      # 控制市场中是否有高频交易者，默认为True【未实现】
* auction_flag = True   # 控制开盘后的市场匹配方式，默认为True，表示连续竞价【未实现】
    
### Statistics
市场统计，可以统计
* 高频交易者的订单提交率
* 高频交易者的订单成交率
* 交易者的财富变化
* 交易者的财富分布
* 闪电崩盘的发生频率
