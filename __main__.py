import discord
import datetime as dt
import requests
from random import randrange, choice
import re
from config import discord_token, api_url


class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_conversation_cache = None
        self.last_message_dt = None
        self.final_message = None
        self.tf_params = {}

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    def determine_conversation(self):
        if self.client_conversation_cache:
            if self.last_message_dt > dt.datetime.now() - dt.timedelta(minutes=20):
                return
        else:
            self.client_conversation_cache = None

    def response_logic(self, message):
        truncate = None
        prefix = None
        length = 1023
        if 'joker' in message.content:
            print('HEHEHEHEHEHEHEHEEHEHEHEHEHEHEHEHEHEHEHE')
            temperature = 1.4
        else:
            temperature = 0.7
        nsamples = 1
        batch_size = nsamples

        return {
            "truncate": truncate,
            "prefix": prefix,
            "nsamples": nsamples,
            "batch_size": batch_size,
            "length": length,
            "temperature": temperature}

    def determine_appropriate_message(self, first_message):
        if first_message:
            # Send longest generated message - it's the most interesting.
            max_len = -1
            choice_index = None
            for idx, message in enumerate(self.client_conversation_cache):
                if len(message) > max_len:
                    max_len = len(message)
                    choice_index = idx
        else:
            choice_index = randrange(len(self.client_conversation_cache))
        self.final_message = self.client_conversation_cache.pop(choice_index)
        return

    async def on_message(self, message):
        if message.author == self.user:
            return
        print('Message received...')

        if 'goodbye' in message.content:
            self.client_conversation_cache = None
            await message.channel.send(choice(['Bye!', 'See ya!', ':terry:']))
            return

        if message.content.lower().startswith('!beta_crim'):
            self.determine_conversation()
            generation_params = self.response_logic(message)
            if not self.client_conversation_cache:
                api_response = requests.post(api_url, generation_params)
                self.client_conversation_cache = api_response.json()
                first_message = True
            else:
                first_message = False
            self.determine_appropriate_message(first_message)
            self.last_message_dt = dt.datetime.now()
            await message.channel.send(self.final_message)


def main():
    client = Client()
    client.run(discord_token)
    # TODO FEATURE - recover on crashed TF session


if __name__ == "__main__":
    main()
