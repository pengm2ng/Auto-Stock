from PyQt5.QtCore import QThread
from algorithms.condition import Condition
from request.dao import Dao
from request.enum.stockEnum import OfferStock
from entity.stock import Stock


class Signal(QThread):
    '''
    시그널 감지 클래스
    '''
    __refresh_time = None  # 조건 새로고침 주기 단위(초)
    __condition_list: list[list[Condition, OfferStock]]   # condition 목록
    __realtime_data_temp = None
    stock: Stock

    def __init__(self):
        pass

    def run(self):
        pass

    def attach_condition(self, condition: Condition, offer) -> None:
        '''
        시그널 이벤트 등록
        '''
        Dao().reg_realtime_slot(self.realtime_data_slot, self.stock)    # 실시간 슬롯에 등록
        self.__condition_list.append([condition, offer])

    def detach_condition(self):
        pass

    def get_condition_list(self):
        return self.__condition_list

    def realtime_data_slot(self, sCode: str, sRealType: str, sRealData: str, sRecordName: str, sPrevNext: str):
        '''
        real time data 이벤트 슬롯

        attribute
        ---------
          BSTR sScrNo,       // 화면번호
          BSTR sRQName,      // 사용자 구분명
          BSTR sTrCode,      // TR이름
          BSTR sRecordName,  // 레코드 이름
          BSTR sPrevNext,    // 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
        '''
        # TODO DAO를 호출해서 GetCommRQData를 받아와야함
        # TODO realtime data 를 가공해야함
        # Dao().
        self.run_condition_trade(self.__realtime_data_temp)

    def run_condition_trade(self, index: int, realtime_data):
        '''
        매도 매수 조건이 만족될 경우, 거래를 진행시킨다.
        '''
        condition_value, offer = self._check_condition(index, realtime_data)
        if condition_value:
            # 조건 충족
            if offer == OfferStock.BUYING:
                # 매수 조건일 때
                Dao().buy_stock()
            else:
                # 매도 조건일 때
                Dao().sell_stock()

    def _check_condition(self, index: int, realtime_data) -> list[bool, OfferStock]:
        '''
        매도, 매수 조건에 맞는지 판별
        '''
        condition = self.__condition_list[index][0]
        return (condition.condition_test(realtime_data), self.__condition_list[index][1])