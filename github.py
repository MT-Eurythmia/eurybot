import text
from feed import FeedPoller

import re

class GithubPoller(FeedPoller):
    """
    Polls a GitHub RSS feed and formats commits
    """
    def parse(self, feed_entry, log_format=False):
        if log_format:
            f_cshort = "[color=#cc0000]%s[/color]"
            f_clong = "[color=#cc0000]%s[/color] ([color=#cc0000]%s[/color])"
            f_all = "[color=#3465a4][git][/color] %s -> [color=#73d216]%s[/color]: [b]%s[/b] [color=#a04265]%s[/color] %s ([color=#888a85]%s[/color])"
        else:
            f_cshort = "\x0304%s\x0f"
            f_clong = "\x0304%s\x0f (\x0304%s\x0f)"
            f_all = "\x0302[git]\x0f %s -> \x0303%s\x0f: \x02%s\x0f \x0313%s\x0f %s (\x0315%s\x0f)"
        committer_realname = feed_entry.authors[0].name
        if committer_realname == "":
            try:
                committer_realname = feed_entry.authors[0].email
            except AttributeError:
                committer_realname = ""
        try:
            committer = feed_entry.authors[0].href.replace('https://github.com/',"")
        except AttributeError:
            committer = committer_realname # This will only use the realname if the nickname couldn't be obtained
        m = re.search(r'/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)/commit/([a-f0-9]{7})', feed_entry.links[0].href)
        repo_name = m.group(1) if m else "?"
        commit_hash = m.group(2) if m else "???????"
        commit_time = feed_entry.updated
        commit_text = feed_entry.title
        commit_link = feed_entry.link
        if committer_realname == "" or committer_realname.lower() == committer.lower():
            committer_final = f_cshort % committer
        else:
            committer_final = f_clong % (committer, committer_realname)
        return f_all % (committer_final, repo_name, commit_text, commit_hash, commit_link, commit_time)
