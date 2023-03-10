import uuid

from pymodm.connection import connect
from pymongo import DESCENDING, ASCENDING
from core.db.mongo_models import Logs, Players, Revolvers
from core.config import WebAppConfig as c
from core.revolver import Revolver

from datetime import datetime, timedelta

import logging
logger = logging.getLogger('root')


class DBManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBManager, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        connect(c.MONGO_CONNECT_URL)
        self.error_log_lvls = ('ERROR', 'CRITICAL')

        #### Players block ####


    def get_player(self, id):
        try:
            p = Players.objects.get({'_id': id})
            return p
        except Players.DoesNotExist:
            return None

    def add_player(self, id, wins = 0, deaths=0):
        if not self.get_player(id):
            return Players(_id=id, wins=wins, deaths=deaths).save()._id
        else:
            return None

    def get_player_wins(self, id):
        try:
            p = Players.objects.get({'_id': id})
            return p.wins
        except Players.DoesNotExist:
            return None

    def get_all_players(self):
        return Players.objects.all()

    def get_player_deaths(self, id):
        try:
            p = Players.objects.get({'_id': id})
            return p.deaths
        except Players.DoesNotExist:
            return None

    def inc_player_deaths(self, id):
        p = self.get_player(id)
        p.deaths = p.deaths + 1
        p.save()

    def inc_player_wins(self, id):
        p = self.get_player(id)
        p.wins = p.wins + 1
        p.save()

    #### Revolvers block ####

    def add_revolver(self, r: Revolver):
        return Revolvers(_id=r.name, descr=r.description, drum_capacity=r.drum_capacity).save()._id

    def get_all_revolvers(self):
        return Revolvers.objects.all()

    def get_revolver(self, id):
        try:
            r = Revolvers.objects.get({'_id': id})
            return r
        except Revolvers.DoesNotExist:
          return None

        #### Logs block ####
    def add_log(self, log_id, time, lineno, pathname, levelname, message):
        """
        time: datetime
        lineno: str
        pathname: str
        levelname: str
        message: str
        return: id of created document
        """
        return Logs(_id=log_id, time=time, lineno=lineno, pathname=pathname, levelname=levelname,
                    message=message).save()._id

    def get_all_logs(self):
        return Logs.objects.all()

    def get_filter_logs(self, query={}, limit=None, offset=None, sort=None, order=None):
        logs = Logs.objects.raw(query).order_by([('time', DESCENDING)])
        count = logs.count()
        if limit is not None and offset is not None:
            logs = logs.skip(offset).limit(limit)
        if sort:
            if order == "asc":
                logs = logs.order_by([(sort, ASCENDING)])
            else:
                logs = logs.order_by([(sort, DESCENDING)])
        return logs, count

    def get_log_by_id(self, log_id):
        try:
            log = Logs.objects.get({'_id': log_id})
            return log
        except Logs.DoesNotExist:
            return None

    def get_daily_logs(self):
        return Logs.objects.raw({
            'time': {'$gte': datetime.today() - timedelta(hours=24)},
        })

    def get_all_error_logs(self):
        return Logs.objects.raw({
            'levelname': {'$in': self.error_log_lvls}
        }).__iter__()