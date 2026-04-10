from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import config
from datetime import datetime

my_db = config.database_uri
alchemy_engine = create_engine(my_db)

class Base(DeclarativeBase): pass

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    message_id = Column(String)
    time_mark = Column(TIMESTAMP)
    ask = Column(String)
    answer = Column(String)
    ok_err_status = Column(Integer)
    tokens_counter = Column(Integer)

class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True)
    st = Column(String)

Base.metadata.create_all(bind = alchemy_engine)
Session = sessionmaker(autoflush=False, bind = alchemy_engine)

def write_wait_record(question_info):
    with Session(autoflush=False, bind = alchemy_engine) as db:
    
        rec_obj = Messages(user_id=question_info[0], 
                           chat_id=question_info[1],
                           message_id='',
                           ask=question_info[2],
                           answer='ответ в процессе обработки',
                           ok_err_status=1,#1=wait(status table)
                           tokens_counter=0,
                           time_mark = datetime.now())
        
        db.add(rec_obj)
        db.commit()
        

def update_ok_record(record_object):
    with Session(autoflush=False, bind = alchemy_engine) as db:
        print(f'id = {record_object.id}')
        work_record = db.query(Messages).filter(Messages.id==record_object.id).first()
        work_record.answer = record_object.answer
        work_record.ok_err_status = 2
        work_record.tokens_counter = 1
        print(f'id {work_record.id} updated')
        #db.flush() #записывает, но не закрывает сессию, зато теперь мы знаем id записи в базу
        db.commit()
        db.close()#---------------&&
        

def read_history(user_id,chat_id):
    with Session(autoflush=False, bind = alchemy_engine) as db:
        last_records = db.query(Messages).\
                        filter(Messages.user_id==user_id, Messages.chat_id==chat_id).\
                        order_by(Messages.time_mark.desc()).\
                        limit(10).\
                        all()
        last_records = last_records[::-1]#переворачиваем от старого к новому
        if len(last_records) == 0:
            hello_record = Messages(user_id = 0, chat_id = 0,
                                    time_mark = datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                                    ask = 'Здесь вы можете ввести свой вопрос',
                                    answer = 'И получить ответ от DeepSeek')
            last_records.append(hello_record)
    return last_records
    
def search_active_asks():
    with Session(autoflush=False, bind = alchemy_engine) as db:
        active_asks = db.query(Messages).\
                        filter(Messages.ok_err_status==1).\
                        order_by(Messages.time_mark.asc()).\
                        limit(10).\
                        all()
                        #здесь фильтр предполагает asc() - от старых к новым 10 записей
    return active_asks

def read_last_record(user_id, chat_id):
     with Session(autoflush=False, bind = alchemy_engine) as db:
        last_record = db.query(Messages).\
                        filter(Messages.user_id==user_id, Messages.chat_id==chat_id).\
                        order_by(Messages.time_mark.desc()).\
                        first()
        return last_record


def fill_status_table():
    st_list = [
        Status(st='wait'),
        Status(st='ok'),
        Status(st='error')
    ]
    with Session(autoflush=False, bind = alchemy_engine) as db:
        try:
            db.add_all(st_list)
            db.commit()
            print('status added')
        except Exception as e:
            db.rollback()
            print(f'error: {e}')
        finally:
            db.close()

if __name__ == '__main__':
    #write_record(1,1,'test_message_id','test_ask','test_answer','ok', 15)
    #records = read_history(2,1)
    #print(f'found {len(records)} records:')
    #for record in records:
    #    print(f'id:{record.id} , at {record.time_mark}')

    #one_record = read_last_record(5,1)
    #print(f'ask: {one_record.ask}')
    #print(f'answer: {one_record.answer}')
    
    #fill_status_table()
    pass