import asyncio
import datetime
import time

import alch_api as messages
import dsc_api as dsc


def search_meek_questions(): #поиск записей с вопросами без ответа
    records = messages.search_active_asks()
    return records


async def ask_async_pack(record_object):
    loop = asyncio.get_event_loop()
    
    def sync_ask_one():
        response = dsc.client.chat.completions.create(
        model = "deepseek-chat",
        messages = [{"role": "user", "content": record_object.ask}])
        result = response.choices[0].message.content
        record_object.answer = result
        record_object.ok_err_status = 2 #2=ok (status table)
        #record_object.tokens_counter = ???
        return record_object

    return await loop.run_in_executor(None, sync_ask_one)
    
async def main(meek_records):
    ready_records = []
    tasks = [ask_async_pack(q) for q in meek_records]
    
    for tasks in asyncio.as_completed(tasks):
        ready_object = await tasks
        ready_records.append(ready_object)
    
    return ready_records


if __name__ == '__main__':
    '''
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y_%m_%d_%H_%M_%S_")
    print(f'begin at: {formatted_date}')
    
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y_%m_%d_%H_%M_%S_")
    print(f'end at: {formatted_date}')
    '''
    
    run=True
    while run==True:
        print('======================')
        meek_records = search_meek_questions()
        print(meek_records)
        if meek_records != []:
            ready_records = asyncio.run(main(meek_records))
            for record in ready_records:
                print(f'id = {record.id}, st = {record.ok_err_status}')
                messages.update_ok_record(record)
                run=False
        else:
            print('0 meet records :)')
            time.sleep(15)