import sys
import pydantic
from typing import Union, Optional
import pandas as pd
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime,timedelta,timezone
from .schemas import *
from .ordersmanagement import PositionManagement
from .enumerations import *

class MT5:
    def __init__(self, symbol, start_date=datetime.now()-timedelta(2), stop_date=datetime.now()-timedelta(days=1)) -> None:
        self.index = 0
        self.data = None
        self.bid = 0
        self.ask = 0
        self.time = datetime.now().timestamp()
        self.spread = 0
        self.symbol_name = symbol
        self.symbol_info_ = None
        self.start_date = start_date.astimezone(timezone.utc).timestamp()
        self.stop_date  = stop_date.astimezone(timezone.utc).timestamp()
        self.tick_info:SymbolTickInfo  = None
        self.positions_terminal = PositionManagement()
        self.TRADE_ACTION_DEAL =  ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL.value
        self.TRADE_ACTION_PENDING = ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING.value
        self.TRADE_ACTION_SLTP = ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP.value
        self.TRADE_ACTION_MODIFY = ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_MODIFY.value
        self.TRADE_ACTION_REMOVE = ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_REMOVE.value
        self.TRADE_ACTION_CLOSE_BY = ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_CLOSE_BY.value
        
        self.ORDER_TYPE_BUY = ENUM_ORDER_TYPE.ORDER_TYPE_BUY.value
        self.ORDER_TYPE_SELL = ENUM_ORDER_TYPE.ORDER_TYPE_SELL.value
        self.ORDER_TYPE_BUY_LIMIT = ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT.value
        self.ORDER_TYPE_SELL_LIMIT = ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT.value
        self.ORDER_TYPE_BUY_STOP = ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP.value
        self.ORDER_TYPE_SELL_STOP = ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP.value
        self.ORDER_TYPE_BUY_STOP_LIMIT = ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT.value
        self.ORDER_TYPE_SELL_STOP_LIMIT = ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT.value
        self.ORDER_TYPE_CLOSE_BY = ENUM_ORDER_TYPE.ORDER_TYPE_CLOSE_BY.value

        self.ORDER_FILLING_FOK = ORDER_TYPE_FILLING.ORDER_FILLING_FOK.value
        self.ORDER_FILLING_IOC = ORDER_TYPE_FILLING.ORDER_FILLING_IOC.value
        self.ORDER_FILLING_BOC = ORDER_TYPE_FILLING.ORDER_FILLING_BOC.value
        self.ORDER_FILLING_RETURN = ORDER_TYPE_FILLING.ORDER_FILLING_RETURN.value

        self.ORDER_TIME_GTC = ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC.value
        self.ORDER_TIME_DAY = ENUM_ORDER_TYPE_TIME.ORDER_TIME_DAY.value
        self.ORDER_TIME_SPECIFIED = ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED
        self.ORDER_TIME_SPECIFIED_DAY = ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED_DAY

        # TRADE RESULT CODES
        self.TRADE_RETCODE_DONE = ENUM_SERVER_RETURN_CODES.TRADE_RETCODE_DONE.value

        if not mt5.initialize():
            raise NotImplemented
        self.symbol_info_ = mt5.symbol_info(symbol)
        self.positions_terminal.symbol_info = self.symbol_info_

        if  self.symbol_info is None:
            raise Exception("symbol data not found")

        history_data = mt5.copy_ticks_range(
            self.symbol_name,
            self.start_date, 
            self.stop_date,
            mt5.COPY_TICKS_ALL
            )

        self.data = pd.DataFrame(history_data)
        self.data = self.data[["time","ask","bid"]].copy()
        self.data["time"] = self.data["time"]
        # print(self.data.head(),"\nHistory data has a size of: ",self.data.shape)
        #shutdown the mt5 terminal
        mt5.shutdown()
        
    def initialize(self,login=0, password=0, server=0):
        return True

    def login(self,**kwargs):
        return True
    #update the terminal informations
    def updateTerminalsInfo(self):
        self.index += 1
        current_line = self.data.iloc[self.index]
        self.ask = current_line.get("ask")
        self.bid = current_line.get("bid")
        self.spread = round((self.ask - self.bid)/self.symbol_info_.point, self.symbol_info_.digits)
        self.time = current_line.get("time")
        self.symbol_info_tick(self.symbol_name)
        #update tick info of position terminal tick
        self.positions_terminal.tick_info = self.tick_info
        #update active positions
        self.positions_terminal.updateOrdersPositions()
        self.positions_terminal.updateActivePositions()

        #update active and history positions total
        self.positions_terminal.positions_total = len(self.positions_terminal.active_positions)
        self.positions_terminal.history_positions_total = len(self.positions_terminal.history_positions)

    ##MT5 STANDARD FUNCTIONS 
    def symbol_info_tick(self, symbol):
        self.tick_info = SymbolTickInfo(
            time=self.time,
            bid=self.bid,
            ask=self.bid,
            last=0,
            volume=0,
            time_msc=self.time*1000,
            flags=0,
            volume_real=0,
            symbol=symbol,
        )
        return self.tick_info
    
    def orders_get(self, symbol="", ticket=0):
        return tuple(self.positions_terminal.orders)

    def positions_get(self, symbol):
        return self.positions_terminal.get_active_positions()

    def positions_total(self):
        return self.positions_terminal.positions_total

    def order_send(self,order_data: dict):
        order_data = MqlTradeRequest.parse_obj(order_data)
        res = self.positions_terminal.openOrder(order_data)
        return res
    
    def symbol_info(self, symbol="eurusd"):
        return self.symbol_info_
    
    def history_deals_get(self, date_from, date_to, group=""):
        return self.positions_terminal.get_history_positions()

    def last_error(self):
        return 3000
    def shutdown(self):
        quit()