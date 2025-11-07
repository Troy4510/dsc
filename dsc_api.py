from deepseek import DeepSeekAPI
from openai import OpenAI
import config

client = OpenAI(api_key = config.dsc_key, base_url = "https://api.deepseek.com/v1")

def ask(question):
    #здесь позже будет процедура проверки на запрещенные слова
    api_ready = api_status()
    if api_ready['is_available']:
        answer = client.chat.completions.create(
            model = "deepseek-chat",
            messages = [{"role": "user", "content": question}])
    
        output = [0,1]
        output.append(answer.id)
        output.append(question)
        output.append(answer.choices[0].message.content)
        output.append('status_ok')
        output.append(answer.usage.completion_tokens)
        return output
    else: 
        print('api error')
        return None
    #print(type(answer))
    #print(dir(answer))
    #print(answer)
    #print(answer.id)
    #print(ask + '\n' + output + '\n')
    #print(f'затрачено токенов: {answer.usage.total_tokens} из них:')
    #print(f'на вопрос (промт): {answer.usage.prompt_tokens}')
    #print(f'на ответ (комплит): {answer.usage.completion_tokens}')

def api_status():
    api_client = DeepSeekAPI(api_key=config.dsc_key)
    balance = api_client.user_balance()
    available = balance['is_available']
    money = balance['balance_infos'][0]['total_balance']
    #print(f'баланс = {money} USD')
    #print(f'доступность: {available}')
    
    return balance

if __name__ == '__main__':
    x = ask('сколько будет 2+2')
    print(x)
    #balance()
    pass