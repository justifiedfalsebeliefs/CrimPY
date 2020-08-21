import gpt_2_simple as gpt2
import os

model_name = "124M"
if not os.path.isdir(os.path.join("models", model_name)):
	print(f"Downloading {model_name} model...")
	gpt2.download_gpt2(model_name=model_name)   # model is saved into current directory under /models/model_name/

csv_file_name = '\plague_hut_strings.csv'

sess = gpt2.start_tf_sess()

gpt2.finetune(sess,
              csv_file_name,
              model_name=model_name,
              steps=1000,
              #sample_every= 50,
              save_every=50
              ,restore_from='latest' #fresh
# run_name #subfolder within checkpoint to save the model. This is useful if you want to work with multiple models (will also need to specify run_name when loading the model
    )
