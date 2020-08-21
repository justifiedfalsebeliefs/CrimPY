import discord
import gpt_2_simple as gpt2
import datetime as dt
from random import randrange
import re
from config import discord_token, run_name, checkpoint_dir


class Utterance:
    def __init__(self, message, tf_params):
        self.message = message
        self.tf_sess = tf_params['tf_sess']
        self.tf_run_name = tf_params['run_name']
        self.tf_checkpoint_dir = tf_params['checkpoint_dir']
        # initialize attributes
        self.generation_params = None
        self.generated_text = None
        self.final_message = None
        self.conversation = None
        self.message_raw = None

    def response_logic(self):
        """All response logic should live here. Puts rules for text generation into generation_params and rules
        for which message to send into send_params."""

        # Determine what text to generate based on message
        truncate = None  # TODO FEATURE determine truncate rules
        prefix = None  # TODO FEATURE determine prefix logic
        length = 1023  # TODO FEATURE determine length gen logic
        if 'joker' in self.message.content:
            print('HEHEHEHEHEHEHEHEEHEHEHEHEHEHEHEHEHEHEHE')
            temperature = 1.4
        else:
            temperature = 0.7
        nsamples = 1
        batch_size = nsamples

        self.generation_params = {
            "sess": self.tf_sess,
            "run_name": self.tf_run_name,
            "checkpoint_dir": self.tf_checkpoint_dir,
            "model_dir": 'models',
            "sample_dir": 'samples',
            "return_as_list": True,
            "truncate": truncate,
            "prefix": prefix,
            "nsamples": nsamples,
            "batch_size": batch_size,
            "length": length,
            "temperature": temperature}
        return

    def gen_text(self):
        """Generates text from params dict"""
        print('Generating message...')
        raw_generated = gpt2.generate(**self.generation_params)
        generated_parsed = re.findall(r'<\|startoftext\|>.+?<\|endoftext\|>', raw_generated[0])
        generated_parsed = [s.replace('<|startoftext|>', '').replace('<|endoftext|>', '') for s in generated_parsed]
        return generated_parsed


class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_conversation_cache = None
        self.last_message_dt = None
        self.final_message = None
        self.tf_params = {}
        self.opener = None

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    def start_tf_session(self, run_name, checkpoint_dir):
        tf_sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(tf_sess, run_name=run_name, checkpoint_dir=checkpoint_dir)
        self.tf_params = {
            "tf_sess": tf_sess,
            "run_name": run_name,
            "checkpoint_dir": checkpoint_dir}

    def determine_conversation(self):
        # Determine if a "conversation" already exists. If there's a conversation, don't generate text and flag it
        if 'goodbye' in self.message_raw.content:
            self.client_conversation_cache = None
            return
        if self.client_conversation_cache:
            if self.last_message_dt > dt.datetime.now() - dt.timedelta(minutes=20):
                return
        else:
            self.client_conversation_cache = None

    def determine_appropriate_message(self):
        """Handles conversation, if one exists. If not, does selection logic from all generated messages.
        TODO FEATURE: could select based on questions, length, content. Or add sentiment analysis and add emotion."""
        if self.opener:
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
        self.message_raw = message
        if message.author == self.user:
            return
        print('Message received...')
        if message.content.lower().startswith('!beta_crim'):
            self.determine_conversation()
            utterance = Utterance(message, self.tf_params)
            utterance.response_logic()
            if not self.client_conversation_cache:
                self.client_conversation_cache = utterance.gen_text()
                self.opener = True
            else:
                self.opener = False
            self.determine_appropriate_message()
            self.last_message_dt = dt.datetime.now()
            await message.channel.send(self.final_message)


def main():
    client = Client()
    client.start_tf_session(run_name, checkpoint_dir)
    client.run(discord_token)
    # TODO FEATURE - recover on crashed TF session
    # TODO FEATURE - refactor TF component as API


if __name__ == "__main__":
    main()
