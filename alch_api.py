from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
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
    ok_err_status = Column(String)
    tokens_counter = Column(Integer)
    

#Base.metadata.create_all(bind = alchemy_engine)
Session = sessionmaker(autoflush=False, bind = alchemy_engine)

def write_record(record_pocket):
    
    with Session(autoflush=False, bind = alchemy_engine) as db:
        rec_obj = Messages(user_id=record_pocket[0], 
                           chat_id=record_pocket[1],
                           message_id=record_pocket[2],
                           ask=record_pocket[3],
                           answer=record_pocket[4],
                           ok_err_status=record_pocket[5],
                           tokens_counter=record_pocket[6],
                           time_mark = datetime.now())
        db.add(rec_obj)
        db.commit()
        
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
    
    
    
    
    
if __name__ == '__main__':
    #write_record(1,1,'test_message_id','test_ask','test_answer','ok', 15)
    records = read_history(2,1)
    print(f'found {len(records)} records:')
    for record in records:
        print(f'id:{record.id} , at {record.time_mark}')
    pass