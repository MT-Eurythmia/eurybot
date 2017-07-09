import feedparser
from github import ParseGitHubCommit

import subprocess

class AutoupdatePoller(object):
    def __init__(self):
        print "Initializing autoupdate poller"

        # Run the submodules finder script
        finder_output = subprocess.check_output(["~/scripts/submodules_finder.sh"])

        self.sources = []
        for submodule_str in finder_output.split(";"):
            splitted = submodule_str.split(",")
            new_entry = {
                "dir": splitted[0],
                "origin": {
                    "URL": splitted[1],
                    "last_seen_id": None
                }
            }
            try:
                new_entry["upstream"] = {
                    "URL": splitted[2],
                    "last_seen_id": None
                }
            except IndexError:
                new_entry["upstream"] = None
            self.sources.append(new_entry)


    def check(self):
        for source in self.sources:
            for line in self._dosource(source["origin"], source["dir"]):
                yield line
            for line in self._dosource(source["upstream"], source["dir"], upstream=True):
                yield line

    def _dosource(self, source, directory, upstream=False):
        result = feedparser.parse(source["URL"])
        result.entries.reverse()
        skipping = True
        for entry in result.entries:
            if (source["last_seen_id"] == entry.id):
                skipping = False
            elif not skipping:
                yield self._doentry(entry, directory, upstream)

        if result.entries:
            source["last_seen_id"] = result.entries[-1].id

    def _doentry(self, entry, directory, upstream):
        msg = "%s\nSubmodule %s was updated on %s. Adding to the to-update file." % (ParseGitHubCommit(entry), directory, "upstream" if upstream else "origin")
        with open('/home/minetest/to_update_submodules.txt', 'a') as file:
            if upstream:
                file.write("%s!\n" % (directory, ))
            else:
                file.write("%s\n" % (directory, ))
