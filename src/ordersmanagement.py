from .schemas import *

class PositionManagement:
    def __init__(self) -> None:
        self.orders = []
        self.active_positions = []
        self.history_positions = []
        self.positions_total = 0
        self.orders_total   = 0
        self.history_positions_total = 0
        self.AccountBalance = 10000
        self.tick_info: SymbolTickInfo  =   None
        self.symbol_info    = None
        self.tickets_generated_counts = 0

    #open trade positions
    def openPosition(self,tick_info:SymbolTickInfo, data: MqlTradeRequest):
        #check for correct stopst
        data = PositionInfoClass.parse_obj(data.__dict__)
        position_type = data.type.value
        
        open_price = tick_info.ask if position_type==0 else (tick_info.bid if position_type==1 else data.price)
        
        if position_type==0 or position_type==4:
            if (data.sl>0 and data.sl>open_price) or (data.tp>0 and data.tp<open_price):
                print("invalid stop specified.")
                return MqlTradeResult(retcode=10006)
        if position_type==1 or position_type==5:
            if (data.sl>0 and data.sl<open_price) or (data.tp>0 and data.tp>open_price):
                print("invalid stop specified.")
                return  MqlTradeResult(retcode=10006)
            
        trade_info_dict:PositionInfoClass = data

        self.tickets_generated_counts += 1
        trade_info_dict.ticket = self.tickets_generated_counts
        trade_info_dict.time  = self.tick_info.time
        
        #check if position type can be accessed if not return
        try:
            if trade_info_dict.type is None:
                raise MqlTradeResult(retcode=10006)
        except:
            return MqlTradeResult(retcode=10006)
        
        if position_type==0 or position_type==1:
            trade_info_dict.active = True
            self.active_positions.append(trade_info_dict)
        elif position_type==4 or position_type==5:
            order_object:OrderInfoClass = OrderInfoClass.parse_obj(trade_info_dict.__dict__)
            order_object.price_open = trade_info_dict.price
            order_object.volume_current = trade_info_dict.volume
            order_object.time_setup = self.tick_info.time
            res = MqlTradeResult.parse_obj(trade_info_dict.__dict__)
            res.retcode = ENUM_SERVER_RETURN_CODES.TRADE_RETCODE_DONE.value
            res.order = trade_info_dict.ticket
            self.orders.append(order_object)
            return  res

        res = MqlTradeResult.parse_obj(trade_info_dict.__dict__)
        res.retcode = ENUM_SERVER_RETURN_CODES.TRADE_RETCODE_DONE.value
        res.order = trade_info_dict.ticket
        return res
    
    def closePosition(self, ticket_number):
        status = False
        for position in self.active_positions:
            myposition: PositionInfoClass = position
            
            if myposition.ticket==ticket_number:
                if myposition.type == 0:
                    myposition = self.updateBuyPosition(myposition)
                elif myposition.type == 1:
                    myposition = self.updateSellPosition(myposition)
                self.AccountBalance += myposition.profit

                myposition.active = False
                myposition.entry = ENUM_DEAL_ENTRY.DEAL_ENTRY_OUT.value
                self.active_positions.remove(myposition)
                self.history_positions.append(myposition)                
                status = True

        if not status:
            print("Did Not find any open position.")
            return MqlTradeResult(retcode=10006)
        return MqlTradeResult(retcode=ENUM_SERVER_RETURN_CODES.TRADE_RETCODE_DONE.value)
    
    def deleteOrder(self, ticket_number):
        status = False
        for order in self.orders:
            myorder: OrderInfoClass = order
            
            if myorder.ticket==ticket_number:
                if myorder.type.value == 4:
                    self.updateBuyOrder(myorder)
                elif myorder.type.value == 5:
                    self.updateSellOrder(myorder)
                if myorder in self.orders:
                    self.orders.remove(myorder)
                status = True

        if not status:
            print("Did Not find any open order with ticket.")
            return MqlTradeResult(retcode=10006)
        
        return MqlTradeResult(retcode=ENUM_SERVER_RETURN_CODES.TRADE_RETCODE_DONE.value)
    
    def updateBuyPosition(self, position_object:PositionInfoClass):
        current_position_price = self.tick_info.ask
        position_object.profit = current_position_price - position_object.price
        position_object.profit = position_object.profit/self.symbol_info.point * position_object.volume

        if current_position_price>position_object.tp or current_position_price<position_object.sl:
            position_object.active = False

        return position_object
    
    def updateSellPosition(self, position_object:PositionInfoClass):        
        current_position_price = self.tick_info.bid
        position_object.profit = position_object.price - current_position_price
        position_object.profit = position_object.profit/self.symbol_info.point * position_object.volume

        if current_position_price>position_object.sl or current_position_price<position_object.tp:
            position_object.active = False

        return position_object

    def updateBuyOrder(self, order_object:OrderInfoClass):
        current_price = self.tick_info.ask
        order_object.price_current = current_price
        if current_price>=order_object.price_open:
            position_object: PositionInfoClass = PositionInfoClass.parse_obj(order_object.__dict__)
            position_object.price = current_price
            position_object.volume = order_object.volume_current
            position_object.type = ENUM_ORDER_TYPE.ORDER_TYPE_BUY
            position_object.time = self.tick_info.time
            position_object.active = True
            self.active_positions.append(position_object)
            self.orders.remove(order_object)
    
    def updateSellOrder(self, order_object:OrderInfoClass):
        current_price = self.tick_info.bid
        order_object.price_current = current_price
        if current_price<=order_object.price_open:
            position_object: PositionInfoClass = PositionInfoClass.parse_obj(order_object.__dict__)
            position_object.price = current_price
            position_object.volume = order_object.volume_current
            position_object.type = ENUM_ORDER_TYPE.ORDER_TYPE_SELL
            position_object.time = self.tick_info.time
            position_object.active = True
            self.active_positions.append(position_object)
            self.orders.remove(order_object)

    def positionMonitor(self, position_object:PositionInfoClass):
        if position_object.active==False:
            self.active_positions.remove(position_object)
            self.history_positions.append(position_object)
            return  
        
        position_type = position_object.type.value
        if position_type==0:
            position_object = self.updateBuyPosition(position_object)
        elif position_type==1:
            position_object = self.updateSellPosition(position_object)
        
        if position_object.active==False:
            self.closePosition(position_object.ticket)

        return position_object

    def orderMonitor(self, order_object:OrderInfoClass):        
        order_type = order_object.type.value
        
        if order_type==4:
            self.updateBuyOrder(order_object)
        elif order_type==5:
            self.updateSellOrder(order_object)

    def updateActivePositions(self):
        for position_object in self.active_positions:
            position_object = self.positionMonitor(position_object)

    def updateOrdersPositions(self):
        for order_object in self.orders:
            self.orderMonitor(order_object)

    def get_active_positions(self):
        positions_active = []
        self.updateActivePositions()

        for position in self.active_positions:
            positions_active.append(position)
        
        return tuple(positions_active)

    def get_orders_positions(self):
        orders_active = []
        for order in self.orders:
            orders_active.append(order)
        return tuple(orders_active)
    
    def get_history_positions(self):
        return tuple(self.history_positions)
    
    def openOrder(self, data:MqlTradeRequest):
        if data.action.value==1:
            res = self.openPosition(self.tick_info, data=data)
            return res
        elif data.action.value == 4:
            res = self.deleteOrder(data.order)
            return res
        