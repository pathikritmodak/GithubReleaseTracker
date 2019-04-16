import atoma
import requests
import slack
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime, timedelta, timezone



REPOS_FILENAME = 'repos.txt'


def get_repos_list(filename):
    if not filename:
        raise Exception("Invalid filename")

    with open(filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


def create_url(repo_name):
    return 'https://github.com/' + repo_name + '/releases.atom'


def get_atom_feed(url):
    return requests.get(url).content


def get_entries_from_parsed_atom_feed(parsed_atom_feed):
    return parsed_atom_feed.entries


def is_datetime_in_last_24h(release_datetime):
    return datetime.now(timezone.utc) - timedelta(hours=72) <= release_datetime


def retrieve_releases_in_last_24h(parsed_atom_feeds):
    entries = list(map(get_entries_from_parsed_atom_feed, parsed_atom_feeds))
    atom_list = []
    for i in range(len(entries)):
        filtered = list(filter(lambda x: is_datetime_in_last_24h(x.updated), entries[i]))
        atom_list.append(filtered)
    atom_list = list(filter(None, atom_list))
    return atom_list


def main():
    repos_list = get_repos_list(REPOS_FILENAME)
    urls = map(create_url, repos_list)
    atom_feeds = map(get_atom_feed, urls)
    parsed_atom_feeds = map(lambda x: atoma.parse_atom_bytes(x), atom_feeds)
    releases_last_24h = list(retrieve_releases_in_last_24h(parsed_atom_feeds))
    version_list = []
    url_list = []
    for i in range(len(releases_last_24h)):
        versions_list = list(map(lambda x: x.title.value, releases_last_24h[i]))
        version_urls = list(map(lambda x: x.links, releases_last_24h[i]))
        version_list.extend(versions_list)
        url_list.extend(version_urls)
    url_decoded_list = []
    for j in range(len(url_list)):
        ver_urls = list(map(lambda x: x.href, url_list[j]))
        url_decoded_list.extend(ver_urls)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(list(zip(version_list, url_decoded_list)),
                 columns=['version', 'url'])
    df['repo'] = df['url'].str.split('/').str[4]

    if len(version_list) < 1:
        print("No new versions released")
    else:
        print('New versions released: ' + '\n' + tabulate(df, headers='keys', tablefmt="psql", showindex=False))
        for i in range(len(df)):
            data = {'version': [df.loc[i, 'version']], 'url' : [df.loc[i, 'url']], 'repo': [df.loc[i, 'repo']]}
            df2 = pd.DataFrame(data, columns=['version', 'url', 'repo'])
            data = np.squeeze(np.asarray(df2))
            slack.send_slack_message(data)


if __name__ == '__main__':
    main()
