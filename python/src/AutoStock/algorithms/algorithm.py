from abc import abstractmethod, ABCMeta
from typing import List
from AutoStock.request.dao import Dao
from AutoStock.request.enum.stockEnum import OfferStock
from AutoStock.algorithms.condition import Condition
from AutoStock.algorithms.signal.signal import Signal
from AutoStock.entity.stock import Stock


class Algorithm(metaclass=ABCMeta):
    '''
    주식 거래 알고리즘 추상클래스
    ===========

    attribute
    ---------
    Algorithm 클래스 하나는 오직 한개의 종목만 거래할 수 있다.
    '''
    __stock: Stock  # 보유 주식
    __money: int    # 예수금
    __signal: Signal    # 시그널
    __refresh_time: int     # Condtion 갱신 주기
    __selling_condition: Condition  # 매도 조건
    __buying_condition: Condition   # 매수 조건

    def __init__(self, stock: Stock, buying_condition: Condition, selling_condition: Condition, refresh_time, money):
        self.__stock = stock
        self.__buying_condition = buying_condition()
        self.__selling_condition = selling_condition()
        self.__signal = Signal(refresh_time, stock, money)
        self.__money = money
        self.__money = 50000

        self.__reg_condition(self.__buying_condition, OfferStock.BUYING)
        self.__reg_condition(self.__selling_condition, OfferStock.SELLING)

    def get_stock(self) -> Stock:
        return self.__stock

    @staticmethod
    def filter_list() -> List[Stock]:
        '''
        거래 대상 주식 필터링
        '''
        raise NotImplementedError

    def get_refresh_time(self) -> int:
        '''
        Condition 갱신 주기

        단위: 초
        '''
        return self.__refresh_time

    def force_selling(self):
        '''
        보유 주식 강제매도
        '''
        Dao().sell_stock(self.__stock)

    @abstractmethod
    def moderate_selling(self):
        '''
        상황 봐가면서 매도하는 메소드

        되도록이면 매도하되, 이건 좀 아니다 싶으면 홀딩한다.
        '''

    def start_algorithm_thread(self):
        '''
        알고리즘 스레드 스타트
        '''
        self._get_signal().start()

    def stop_algorithm_thread(self):
        self._get_signal().exit()   # 스레드 종료

    def _get_signal(self) -> Signal:
        return self.__signal

    def __reg_condition(self, condition: Condition, offer):
        '''
        Condition 등록 위임 메소드
        '''
        self.__signal.attach_condition(condition, offer)
