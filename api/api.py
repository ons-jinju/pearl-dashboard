import logging
import os

from flask import Blueprint

from idcube_hive_connector import connector
from idcube_python_utils import mails
from infrabot_diy_python_client import diy_client

logger = logging.getLogger(__name__)
api = Blueprint('api', __name__, template_folder='templates')


@api.route('/', methods=['POST', 'GET'])
def liveness_probe():
    return "I am alive"


@api.route('/helloworld', methods=['POST', 'GET'])
def hello_world():
    msg = "Hello World"
    print(msg)
    logger.info(msg)
    return msg


@api.route('/query', methods=['POST', 'GET'])
def query():
    conn = connector.connect_idcube_athena()
    cursor = conn.cursor()
    sql = """  
select skt_oper_hdofc_org_nm, sum(dn_size)*8/(sum(dn_thp_time)/1000000)/1048576 dn_thp_speed,
sum(up_size)*8/ (sum(up_thp_time)/1000000) /1048576 up_thp_speed, sum(user_cnt) user_count
from d_smf.dsmf_youtube_comm_qlt_anal_1h
where dt='20240716' and hh='15'
group by skt_oper_hdofc_org_nm;
"""
    cursor.execute(sql)
    df = cursor.fetchall()
    return df.to_json()


@api.route('/mail', methods=['POST', 'GET'])
def mail():
    rcpr = [mails.MailRecipient(name='조민정', addr='hjmj1025.cho@sk.com')]
    mails.send_mail('Playground TEST', 'Playground TEXT', rcpr, text_vars={})
    return 'ok'


@api.route('/telegram', methods=['POST', 'GET'])
def telegram():
    diy_client.send_telegram_message("chat_or_group_id", "testtest")
    return 'ok'