import json

class TelegramAPIWrapper():
  
  base_template = """https://api.telegram.org/bot{bot_token}/"""

  #below are appends to base_template
  # send_msg_template = """sendMessage?chat_id={chat_id}"""
  send_reply_template = """sendMessage?chat_id={chat_id}&text={reply}"""
  send_msg_keyboard = """sendMessage?chat_id={chat_id}&parse_mode=Markdown&reply_markup={rmkup}"""
  get_updates = """getUpdates?timeout={t_out}"""
  get_updates_offset = """getUpdates?timeout={t_out}&offset={offset}"""

  def __init__(self, token=None):
    self.token = token
    self.base_template = self.base_template.format(bot_token=token)

  def get_updates_url(self,offset=None,timeout=100):
    update_ret_val = self.base_template
    if not offset:
      update_ret_val += self.get_updates.format(t_out=timeout)
    else:
      update_ret_val += self.get_updates_offset.format(t_out=timeout,offset=offset)

    return update_ret_val


  def send_message_url(self,chat_id,text):
    # print(chat_id)
    return self.base_template + self.send_reply_template.format(
                                  chat_id=chat_id, reply=text)

  def send_keyboard_url(self,chat_id,keyboard_options):
    keyboard = [[option] for option in options] 
    markup = {"keyboard": keyboard, 
              "one_time_keyboard": True}
    
    return self.base_template + self.send_msg_keyboard.format(
                                  chat_id=chat_id, rmkup=json.dumps(markup))
