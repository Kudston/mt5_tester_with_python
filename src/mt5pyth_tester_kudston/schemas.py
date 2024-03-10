import sys
import pydantic
from datetime import datetime
from typing import Optional, Union
from .enumerations import *

class ParentPydanticModel(pydantic.BaseModel):
    class Config:
        orm_mode = True

class PositionInfoClass(ParentPydanticModel):
    ticket: Optional[int] 
    time: Optional[int]
    type: Union[int, ENUM_ORDER_TYPE]
    magic: Optional[int] 
    identifier: Optional[int] 
    reason: Optional[int]
    volume: Optional[float]
    price: Optional[float]
    sl: float
    tp: float
    price_current: Optional[float]
    swap: Optional[float]
    profit: Optional[float]
    symbol: str
    comment: Optional[str]
    entry: Optional[int]
    active: bool = True

class OrderInfoClass(ParentPydanticModel):
    ticket: int
    time_setup: Optional[int]
    time_setup_msc: Optional[int]
    time_expiration: Optional[int]
    type:           ENUM_ORDER_TYPE
    type_time:  Optional[ENUM_ORDER_TYPE_TIME]
    type_filling: Optional[ORDER_TYPE_FILLING]
    state: Optional[int]
    magic: Optional[int]
    volume_current: Optional[float]
    price_open: Optional[float]
    sl: float
    tp: float
    price_current: Optional[float]
    symbol: Optional[str]
    comment: Optional[str]
    external_id: Optional[int]

class SymbolTickInfo(ParentPydanticModel):
    time:int 
    bid:float
    ask:float 
    last:float 
    volume:int
    time_msc:int
    flags:int
    volume_real:int
    symbol: str

class MqlTradeRequest(ParentPydanticModel):
    action: ENUM_TRADE_REQUEST_ACTIONS           # Trade operation type
    magic:  Optional[int]                                  # Expert Advisor ID (magic number)
    order:  Optional[int]                                  # Order ticket
    symbol: Optional[str]                                  # Trade symbol
    volume: Optional[float]                                # Requested volume for a deal in lots
    price:  Optional[float]                                # Price
    stoplimit:  Optional[float]                            # StopLimit level of the order           
    sl:     Optional[float]                                # Stop Loss level of the order
    tp:     Optional[float]                                # Take Profit level of the order
    deviation:  Optional[float]                            # Maximal possible deviation from the requested price
    type:     Optional[ENUM_ORDER_TYPE]                                # Order type
    type_filling: Optional[ORDER_TYPE_FILLING]             # Order execution type
    type_time:      Optional[int]                          # Order expiration type
    expiration:    Optional[int]                           # Order expiration time (for the orders of ORDER_TIME_SPECIFIED type)
    comment:       Optional[str]                           # Order comment
    position:      Optional[int]                           # Position ticket
    position_by:   Optional[int]                           # The ticket of an opposite position

class MqlTradeResult(ParentPydanticModel):
  retcode: Optional[int]         ## Operation return code
  deal:    Optional[int]             ## Deal ticket, if it is performed
  order:   Optional[int]             ## Order ticket, if it is placed
  volume:  Optional[float]           ## Deal volume, confirmed by broker
  price:   Optional[float]           ## Deal price, confirmed by broker
  bid:     Optional[float]           ## Current Bid price
  ask:     Optional[float]           ## Current Ask price
  comment: Optional[str]             ## Broker comment to operation (by default it is filled by description of trade server return code)
  request_id: Optional[int]          ## Request ID set by the terminal during the dispatch 
  retcode_external:  Optional[int]      ## Return code of an external trading system