import copy

from flask import Blueprint, jsonify, render_template

from app.utils import *


bp = Blueprint('views', __name__)


meta = load_json_file(['data', 'meta.json'])
classes = load_json_file(['data', 'classes.json'])
functions = load_json_file(['data', 'functions.json'])
prompts = load_json_file(['data', 'prompts.json'])
classes_level = load_json_file(['data', 'class_level.json'])


# get function dict:
functions_dict = {f['function']: f for f in functions}


# class id to names,
#{ "code_development": {"eng": Code Development, "chn": "代码开发"}, ...}
cid_to_cnames = {}
for c in classes:
    cid = c['id']
    cid_to_cnames[cid] =c['names']




# function id to class name
# {'function_id': [{"eng": Code Development, "chn": "代码开发"}, ...]}
fid_to_cnames = {}
for f in functions:
    fid = f['function']
    cid_lst = f['class'] # a function can have many classes
    cnames_lst = [cid_to_cnames[cid] for cid in cid_lst]
    fid_to_cnames[fid] = cnames_lst


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/fetch_meta/<meta_name>')
def fetch_meta(meta_name):
    return jsonify({"content": meta[meta_name], "message": "success"})


@bp.route('/fetch_class/<param>')
def fetch_class(param):
    if param == 'with_example':
        result = []
        for item in copy.deepcopy(classes):
            one_class = item
            class_id = one_class['id']
            for function in functions: # 遍历所有的function，找到属于某个class的function
                if class_id in function['class']:
                    one_class['example'] = function
                    break
            result.append(one_class)
    elif param == 'raw':
        result = classes
    else:
        return jsonify({"message": f'Invalid parameter "{param}"'})
    return jsonify({"content": result, "message": "success"})


# @bp.route('/fetch_meta/<meta_name>')
# def fetch_class_(meta_name):
#     return jsonify({"content": meta[meta_name], "message": "success"})


# By Haomin Wen
@bp.route('/fetch_tree/')
def fetch_tree():

    result = copy.deepcopy(classes_level)

    return jsonify({"content": result, "message": "success"})

@bp.route('/fetch_prompt/<class_id>/<lan_code>')
def fetch_prompt(class_id, lan_code):
    result = []

    # find all funcions that has the class
    if class_id == 'all_class':
        f_lst = [f['function'] for f in functions]
    else:
        f_lst = [f['function'] for f in functions if class_id in f['class']]

    # find all prompts that has the function
    for data in prompts:
        fid = data['function']
        if fid not in f_lst: continue
        for p in data['content'][lan_code]:
            tmp = {}
            tmp['chat_list'] =  p['content'] #todo: change later
            tmp['class_list'] = [name[lan_code] for name in fid_to_cnames[fid]] # get class names
            tmp['author'] = '@w'
            tmp['model'] = 'GPT 3.5'
            tmp['function_desc'] = functions_dict[fid]['desc'][lan_code]
            #priority_check todo: excute the priority check here
            result.append(tmp)
    return jsonify({"content": result, "message": "success"})




@bp.route('/search_prompt/<search_text>/<lan_code>')
def search_prompt(search_text, lan_code):
    result = []

    for data in prompts:
        fid = data['function']
        for p in data['content'][lan_code]:
            p_text = p['content'][0]

            score  = text_similarity_score(search_text, p_text, lan_code)
            if score > 0.5:
                tmp = {}
                tmp['chat_list'] = p['content']  # todo: change later
                tmp['class_list'] = [name[lan_code] for name in fid_to_cnames[fid]]  # get class names
                tmp['author'] = '@w'
                tmp['model'] = 'GPT 3.5'
                tmp['function_desc'] = functions_dict[fid]['desc'][lan_code]
                result.append(tmp)
    return jsonify({"content": result, "message": "success"})


from waitress import serve
app = Flask(__name__)















