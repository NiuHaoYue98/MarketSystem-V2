#提交的订单
class Order:
    traderID = 0        #交易者编号
    direction = 0       #订单方向 >0 1表示买单,0 表示卖单
    scale = 0           #指令规模
    price = 0           #指令价格
    time = 0            #提交时间
    suspend_time = 0    #剩余时间
    pi = 0              #单笔订单的收益

#成交的订单
class Deal:
    time = 0            #成交时间
    askID = ''          #卖方ID
    bidID = ''          #买方ID
    price = 0           #成交价
    scale = 0           #成交量
    asktime = 0         #买方订单提交时间
    bidtime = 0         #卖方订单提交时间
    askprice = 0        #买方订单价格
    bidprice = 0        #卖方订单价格
    askscale = 0        #买方订单规模
    bidscale = 0        #卖方订单规模

