import requests
import numpy as np
import pandas as pd

WIKIPEDIA_API_ENDPOINT = 'https://www.coppermind.net/w/api.php'
DATA_FILE = 'coppermind_editors.csv'
    
def get_editor_names(names, start=None, chunk_size=100):
    params = {
        'action': 'query',
        'list': 'allusers',
        'aufrom': start,
        'aulimit': chunk_size,
        'auwitheditsonly':'',
        'format': 'json',
        'formatversion': 2,  # version 2 is easier to work with
    }
    payload = requests.get(WIKIPEDIA_API_ENDPOINT, params=params).json()
    users = payload["query"]["allusers"]
    names += [user["name"] for user in users]
    if len(users) < chunk_size:
        return list(set(names))
    else:
        last = users[-1]["name"]
        return get_editor_names(names, last, chunk_size)
    
def get_editor_rev_ids_by_name(user_name, ids, start=None, chunk_size=100):
    params = {
        'action': 'query',
        'list': 'usercontribs',
        'ucstart': start,
        'uclimit': chunk_size,
        'ucuser': [user_name],
        'format': 'json',
        'formatversion': 2,  # version 2 is easier to work with
    }
    payload = requests.get(WIKIPEDIA_API_ENDPOINT, params=params).json()
    contribs = payload["query"]["usercontribs"]
    ids += [contrib["revid"] for contrib in contribs]
    if len(contribs) < chunk_size:
        return list(set(ids))
    else:
        last = contribs[-1]["timestamp"]
        return get_editor_rev_ids_by_name(user_name, ids, last, chunk_size)
    
def sample_from_list(ls, x=10):
    return list(np.random.choice(ls,x,False))

def build_dataframe(users):

    data = []

    for user in users:
        row = []
        rev_ids = get_editor_rev_ids_by_name(user, [])
        row.append(user)
        row.append(len(rev_ids))
        row.append(rev_ids)
        data.append(row)

    df = pd.DataFrame.from_records(data, columns=["user name", "number of revisions", "revision ids"])
    return df

def eliminate_blocked_users(df):
    return df[df["number of revisions"]!=0]

def write_dataframe_to_file(df, filename=DATA_FILE):
    f = open(filename, 'w')
    df.to_csv(f)
    f.close()

def read_dataframe_from_file(filename=DATA_FILE):
    f = open(filename, 'r')
    df = pd.DataFrame.from_csv(f)
    f.close()
    return df

def get_sample_revisions(df, sample_size=25):
    df = df[df["number of revisions"] >= 10]
    random_editors = df.sample(sample_size)
    d = {}
    for row in random_editors.itertuples(index=True):
        d[getattr(row, "_1")] = list(np.random.choice(eval(getattr(row, "_3")),10,False))
    return d

def get_revision_diff(rev_id):
    params = {
        'action': 'query',
        'prop': 'revisions',
        'revids': rev_id,
        'rvdiffto' : 'prev',
        'format': 'json',
        'formatversion': 2,  # version 2 is easier to work with
    }
    payload = requests.get(WIKIPEDIA_API_ENDPOINT, params=params).json()
    return payload["query"]["pages"][0]["revisions"][0]["diff"]["body"]

def write_diff_files(d):
    for (k, v) in d.items():
        for rev_id in v:
            filename = "diff_" + k + "_" + str(rev_id) + ".html"
            f = open(filename, 'w')
            f.write(get_revision_diff(rev_id))
            f.close()

# MAIN FUNCTION
def main():
#    users = get_editor_names([])
#    df = build_dataframe(users)
#    write_dataframe_to_file(eliminate_blocked_users(df))
    df = read_dataframe_from_file()
    d = get_sample_revisions(df)
    write_diff_files(d)


if __name__ == '__main__':
    main()
