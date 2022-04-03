try:
    from .const import (  # isort:skip
        __nameMyEnedis__,
    )

except ImportError:
    from const import (  # type: ignore[no-redef]
        __nameMyEnedis__,
    )

import logging

from .myCheckData import myCheckData
from .myDataControl import getInformationDataControl, okDataControl

log = logging.getLogger(__nameMyEnedis__)


class myDataEnedisByDay:
    def __init__(self, myCalli, token, version, contrat):
        self.myCalli = myCalli
        self._value = 0
        self._date = None
        self._contrat = contrat
        self._token, self._version = token, version
        self._dateDeb = None
        self._dateFin = None
        self._callOk = None
        self._nbCall = 0
        self._data = None

    def CallgetData(self, dateDeb, dateFin):
        val1, val2 = self.myCalli.getDataPeriod(dateDeb, dateFin)
        return val1, val2

    def getValue(self):
        return self._value

    def getDateFin(self):
        return self._dateFin

    def getDateDeb(self):
        return self._dateDeb

    def getCallOk(self):
        return self._callOk

    def getNbCall(self):
        return self._nbCall

    def updateData(
        self,
        clefFunction,
        horairePossible=True,
        data=None,
        dateDeb=None,
        dateFin=None,
        withControl=False,
        dataControl=None,
    ):
        self._nbCall = 0
        onLance = True
        if withControl:
            if okDataControl(clefFunction, dataControl, dateDeb, dateFin):
                onLance = True
                self._callOk = True
            else:
                if not horairePossible:
                    onLance = True
                    dateDeb, dateFin, self._callOk = getInformationDataControl(
                        dataControl
                    )
                    if self._callOk is None:
                        data = (
                            None  # si on doit mettre à jour .... sauf si on est pas la
                        )
                else:
                    self._callOk = None
                    data = None  # si on doit mettre à jour .... sauf si on est pas la

        if onLance:
            self._dateDeb = dateDeb
            self._dateFin = dateFin
            log.info(f"--updateData {clefFunction} ( du {dateDeb} au {dateFin} )--")
            self._data = data
            if self._data is None:
                if dateDeb == dateFin:
                    self._value = 0
                else:
                    self._data, callDone = self.CallgetData(dateDeb, dateFin)
                    if (callDone) and (myCheckData().checkDataPeriod(self._data)):
                        self._value = myCheckData().analyseValueAndAdd(self._data)
                        self._callOk = True
                        self._nbCall = 1
                    else:
                        self._value = 0
                    self._callOk = callDone
            else:
                callDone = True
                if (callDone) and (myCheckData().checkDataPeriod(self._data)):
                    self._value = myCheckData().analyseValueAndAdd(self._data)
                    self._callOk = True
                else:
                    self._value = 0
                self._callOk = callDone
            log.info(f"with update !! {clefFunction} ( du {dateDeb} au {dateFin} )--")
            log.info(f"updateData : data {self._data}")
        else:
            log.info(f"noupdate !! {clefFunction} ( du {dateDeb} au {dateFin} )--")
            log.info(f"no updateData : data {self._data}")
        return self._data
