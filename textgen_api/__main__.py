import flask
import re
import gpt_2_simple as gpt2
from flask import request, jsonify
from config import run_name, checkpoint_dir

app = flask.Flask(__name__)

@app.route('/generate_text', methods=['POST'])
def generate_text():
    tf_sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(tf_sess, run_name=run_name, checkpoint_dir=checkpoint_dir)
    generation_params = request.args.to_dict()
    generation_params["sess"] = tf_sess
    generation_params["checkpoint_dir"] = checkpoint_dir
    generation_params["return_as_list"] = True
    print('Generating message...')
    raw_generated = gpt2.generate(**generation_params)
    # Post-process formatting
    generated_parsed = re.findall(r'<\|startoftext\|>.+?<\|endoftext\|>', raw_generated[0])
    generated_parsed = [s.replace('<|startoftext|>', '').replace('<|endoftext|>', '') for s in generated_parsed]
    generated_parsed = [s for s in generated_parsed if len(s) > 25]
    return jsonify(generated_parsed)


if __name__ == '__main__':
    app.run(debug=False)

