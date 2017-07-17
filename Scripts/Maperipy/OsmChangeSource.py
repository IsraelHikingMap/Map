"""OSM change file sources for incremental Tile update
Dependencies:
- osmupdate: https://wiki.openstreetmap.org/wiki/Osmupdate
- osmconvert: https://wiki.openstreetmap.org/wiki/Osmconvert
- wget: Windows: http://gnuwin32.sourceforge.net/packages/wget.htm
        Linux: built-in
"""

import os
import errno
from maperipy import *
from datetime import *

class osmChangeSource(object):
    """Providing a web-based source for OSM change files.
    The default server is planet.openstreetmap.org
    """

    def __init__(self, base, changes, updated, tempdir, region="planet"):
        self.base = base  # Existing OSM file or previous OsmChange file
        self.changes = changes  # OsmChange file
        self.updated = updated  # Updated OSM file
        self.tempdir = tempdir
        self.mkdir_p(tempdir)
        self.region = region
        self.tempfiles = os.path.join(self.tempdir, "temp")
        self.base_url = "https://planet.openstreetmap.org/"
        self.latest_url = self.base_url + "pbf/planet-latest.osm.pbf"
        self.updates_url = self.base_url + "replication/"
        self.change_resolution = ""
        self.osmupdate_params = []
        self.osmconvert_params = []

    def status(self):
        if os.path.exists(self.updated):
            if os.path.exists(self.changes):
                return "incremental"
            else:
                return "non-incremental"
        elif os.path.exists(self.changes):
            return "changes"
        elif os.path.exists(self.base):
            return "base"
        elif os.path.exists(self.changes+".old"):
            return "idle"
        else:
            return "uninitialized"

    def downloadBase(self):
        App.log("=== Downloading "+self.region+" latest map data ===")
        self.silent_remove(self.base)
        self.silent_remove(self.updated)
        self.silent_remove(self.changes)
        self.silent_remove(self.changes+".old")
        # wget for Windows: http://gnuwin32.sourceforge.net/packages/wget.htm
        exit_code = App.run_program(
                'wget.exe', 7200, ["--no-directories", "--no-verbose",
                    "-O", self.updated, self.latest_url])
        if exit_code:
            self.silent_remove(self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def downloadChange(self):
        # return codes:
        # 0 - download successful
        # 21 - osmupdate: Your OSM file is already up-to-date.
        # otherwise - error
        App.log("=== Downloading "+self.region+" map updates ===")
        status = self.status()
        if status == "base":
            base = self.base
        elif status == "idle":
            base = self.changes+".old"
        else:
            App.log('Should not download changes for {} in status "{}".'.format(
                self.region, status))
            raise RuntimeError
        exit_code = App.run_program(
                "osmup.exe", 21600, [base, self.changes,
                        "--base-url="+self.updates_url,
                        self.change_resolution,
                        "--tempfiles="+self.tempfiles]
                    + self.osmupdate_params) 
        if exit_code not in [0, 21]:
            self.silent_remove(self.changes)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def downloadUpdate(self):
        # return codes:
        # 0 - download successful
        # 21 - osmupdate: Your OSM file is already up-to-date.
        # otherwise - error
        status = self.status()
        if status == "uninitialized":
            App.log("=== Non-incremental Tile Generation ===")
            return self.downloadBase()
        elif status == "base":
            return self.downloadChange() or self.createUpdate()
        else:
            App.log('Should not download an update for {} in status "{}".'.format(
                self.region, status))
            raise RuntimeError

    def createUpdate(self):
        # Create updated OSM file given an base OSM file and its changes
        App.log("=== Creating updated "+self.region+" map data ===")
        if not os.path.exists(self.base):
            App.log('Cannot create an update for {}: missing base file "{}".'.format(
                self.region, self.base))
        if not os.path.exists(self.changes):
            App.log('Cannot create an update for {}: missing changes file "{}".'.format(
                self.region, self.changes))
        exit_code = App.run_program(
                "osmconvert.exe", 7200, [self.base, self.changes, "-o="+self.updated]
                + self.osmconvert_params)
        if exit_code:
            self.silent_remove(self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def advance(self):
        App.log("=== Advancing "+self.region+" map state ===")
        status = self.status()
        if status == "incremental":
            self.safe_rename(self.updated, self.base)
            self.silent_remove(self.changes)
        elif status == "non-incremental":
            self.safe_rename(self.updated, self.base)
        elif status == "changes":
            self.safe_rename(self.changes, self.changes+".old")
            self.silent_remove(self.base)
        elif status == "base":
            return
        else:
            App.log('Should not advance {} in status "{}".'.format(
                self.region, status))
            raise RuntimeError

    def deactivate(self):
        self.silent_remove(self.updated)
        self.silent_remove(self.changes)

    def timestamp(self, file):
        if not os.path.exists(file):
            return datetime.min
        cmd = ["osmconvert.exe", "--out-timestamp", file]
        stdout, stderr, exit_code = self.run_command(cmd)
        if exit_code:
            App.log(stderr)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
            raise RuntimeError
        result = stdout.splitlines()[0]
        if result != "(invalid timestamp)":
            return datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")
        result = self.statistics(file)
        if "timestamp max" in result:
            return datetime.strptime(result["timestamp max"], "%Y-%m-%dT%H:%M:%SZ")
        return datetime.min

    def statistics(self, file):
        cmd = ["osmconvert.exe", "--out-statistics", file]
        stdout, stderr, exit_code = self.run_command(cmd)
        if exit_code:
            App.log(stderr)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
            raise RuntimeError
        return dict(line.split(": ") for line in stdout.splitlines())

    def mkdir_p(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)

    # Based on https://www.python.org/dev/peps/pep-3151/#lack-of-fine-grained-exceptions
    def silent_remove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def silent_rename(self, filename, new_filename):
        self.silent_remove(new_filename)
        try:
            os.rename(filename, new_filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def safe_rename(self, filename, new_filename):
        self.silent_remove(new_filename+".recovery")
        self.silent_rename(new_filename, new_filename+".recovery")
        try:
            os.rename(filename, new_filename)
            self.silent_remove(new_filename+".recovery")
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    # Based on http://www.ironpython.info/index.php?title=Launching_Sub-Processes
    def run_command(self, args, input=None):
        from System.Diagnostics import Process
        p = Process()
        have_stdin = input is not None
        p.StartInfo.UseShellExecute = False
        p.StartInfo.RedirectStandardInput = have_stdin
        p.StartInfo.RedirectStandardOutput = True
        p.StartInfo.RedirectStandardError = True
        p.StartInfo.CreateNoWindow = True
        p.StartInfo.FileName = args[0]

        # not a precise way to join these! See list2cmdline in CPython's subprocess.py for the proper way.
        p.StartInfo.Arguments = " ".join(args[1:])

        App.log("  Running command: " + " ".join(args))
        p.Start()
        if have_stdin:
            p.StandardInput.Write(input)
        p.WaitForExit() 
        stdout = p.StandardOutput.ReadToEnd()
        stderr = p.StandardError.ReadToEnd()
        return stdout, stderr, p.ExitCode

class geofabric(osmChangeSource):
    """Source based on a region of the geofabrik.de replication server
    Example:
    osm_source = geofabric(
            os.path.join('Cache', 'israel-and-palestine-latest.osm.pbf'),
            os.path.join('Cache', 'israel-and-palestine-update.osc'),
            os.path.join('Cache', 'israel-and-palestine-updated.osm.pbf'),
            os.path.join('Cache', 'geofabrik')
            "asia/israel-and-palestine")
    """
    def __init__(self, base, changes, updated, tempdir, region):
        osmChangeSource.__init__(self, base, changes, updated, tempdir, region)
        self.tempfiles = os.path.join(self.tempdir, os.path.normcase(self.region))
        self.base_url = "http://download.geofabrik.de/"
        self.latest_url = self.base_url + self.region + "-latest.osm.pbf"
        self.updates_url = self.base_url + self.region + "-updates"
        self.change_resolution = "--sporadic"

class openstreetmap_fr(osmChangeSource):
    """Source based on a region of the openstreetmap.fr replication server
    Example:
    osm_source = openstreetmap_fr(
            os.path.join('Cache', 'israel-latest.osm.pbf'),
            os.path.join('Cache', 'israel-update.osc'),
            os.path.join('Cache', 'israel-updated.osm.pbf'),
            os.path.join('Cache', 'openstreetmap_fr'),
            "asia/israel"))
    """
    def __init__(self, base, changes, updated, tempdir, region):
        osmChangeSource.__init__(self, base, changes, updated, tempdir, region)
        self.tempfiles = os.path.join(self.tempdir, os.path.normcase(self.region))
        self.base_url = "http://download.openstreetmap.fr/"
        self.latest_url = self.base_url + "extracts/" + self.region + ".osm.pbf"
        self.state_url = self.base_url + "extracts/" + self.region + ".state.txt"
        self.updates_url = self.base_url + "replication/" + self.region
        self.change_resolution = "--minute"

    def downloadBase(self):
        self.silent_remove(self.base)
        self.silent_remove(self.updated)
        self.silent_remove(self.changes)
        self.silent_remove(self.changes+".old")
        # The timestamp must be downloaded separately and added ro the diff
        timestamped_base = os.path.join(os.path.dirname(self.updated),
                "timestamped."+os.path.basename(self.updated))
        cmd = ["wget", "-O", "-", self.state_url]
        stdout, stderr, exit_code = self.run_command(cmd)
        if exit_code:
            App.log(stderr)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
            return exit_code
        timestamp = "--timestamp="+(stdout.splitlines()[2].replace("\\", ""))
        exit_code = osmChangeSource.downloadBase(self) or App.run_program(
                "osmconvert.exe", 7200,
                [self.updated, 
                "-o="+timestamped_base, timestamp]
                + self.osmconvert_params)
        self.silent_remove(self.updated)
        if exit_code:
            self.silent_remove("timestamped."+self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        else:
            os.rename(timestamped_base, self.updated)
        return exit_code

class osmChangeSourceMerge(osmChangeSource):
    """Source made by merging multiple sub-regions.
    Sub-regions are processed in the order they were added.
    Sub-regions can contain sub-regions of their own.
    Example:
    osm_source = osmChangeSourceMerge(
            os.path.join('Cache', 'israel-and-palestine-latest.osm.pbf'),
            os.path.join('Cache', 'israel-and-palestine-update.osc'),
            os.path.join('Cache', 'israel-and-palestine-updated.osm.pbf'),
            "asia/israel-and-palestine")
    osm_source.addSource(openstreetmap_fr(
            os.path.join('Cache', 'palestine-latest.osm.pbf'),
            os.path.join('Cache', 'palestine-update.osc'),
            os.path.join('Cache', 'palestine-updated.osm.pbf'),
            os.path.join('Cache', 'openstreetmap_fr'),
            "asia/palestine"))
    osm_source.addSource(openstreetmap_fr(
            os.path.join('Cache', 'israel-latest.osm.pbf'),
            os.path.join('Cache', 'israel-update.osc'),
            os.path.join('Cache', 'israel-updated.osm.pbf'),
            os.path.join('Cache', 'openstreetmap_fr'),
            "asia/israel"))
    
    """
    def __init__(self, base, changes, updated, region):
        # Merge sources do not use a tempdir as there is no direct download
        # from servers
        osmChangeSource.__init__(self, base, changes, updated, ".", region)
        del self.tempfiles, self.tempdir
        self.sources = []

    def addSource(self, source):
        self.sources.append(source)

    def downloadBase(self):
        App.log("=== Downloading "+self.region+" latest map data ===")
        self.silent_remove(self.base)
        self.silent_remove(self.updated)
        self.silent_remove(self.changes)
        self.silent_remove(self.changes+".old")
        if not self.sources:
            App.log('No sources defined for {}.'.format(
                self.region))
            raise RuntimeError
        for source in self.sources:
            exit_code = source.downloadBase() or App.run_program(
                    "osmconvert.exe", 16200,
                    [source.updated,"-o="+source.updated+".o5m"]
                    + self.osmconvert_params)
            if exit_code:
                return exit_code
        App.log("=== Merging "+self.region+" latest map data ===")
        earliest = "--timestamp={}Z".format(
            min(map(lambda source:source.timestamp(source.updated),
                self.sources)).isoformat())
        exit_code = App.run_program(
                "osmconvert.exe", 7200,
                map(lambda source:source.updated+".o5m", self.sources)
                + ["-o="+self.updated, earliest]
                + self.osmconvert_params)
        if exit_code:
            self.silent_remove(self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        else:
            for source in self.sources:
                self.silent_remove(source.updated+".o5m")
        return exit_code

    def downloadChange(self):
        App.log("=== Downloading "+self.region+" map changes ===")
        if not self.sources:
            App.log('No sources defined for {}.'.format(
                self.region))
            raise RuntimeError
        status = self.status()
        if status not in ["idle", "base"]:
            App.log('Should not download changes for {} in status "{}".'.format(
                self.region, status))
            raise RuntimeError
        for source in self.sources:
            source.deactivate()
            exit_code = source.downloadChange()
            if exit_code not in [0, 21]:
                return exit_code
        App.log("=== Merging "+self.region+" latest map data ===")
        earliest = "--timestamp={}Z".format(
            min(map(lambda source:source.timestamp(source.changes),
                self.sources)).isoformat())
        exit_code = App.run_program(
                "osmconvert.exe", 7200,
                map(lambda source:source.changes, self.sources)
                + ["-o="+self.changes, earliest]
                + self.osmconvert_params)
        if exit_code:
            self.silent_remove(self.changes)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def advance(self):
        if not self.sources:
            App.log('No sources defined for {}.'.format(
                self.region))
            raise RuntimeError
        osmChangeSource.advance(self)
        for source in self.sources:
            source.advance()

    def consistent(self):
        if not self.sources:
            App.log('No sources defined for {}.'.format(
                self.region))
            return False
        status = self.status()
        if status in ["incremental", "changes"]:
            for source in self.sources:
                source_status = source.status()
                if source_status != "changes":
                    App.log('Sub-source {} in "{}" state while {} in "{}" state'.format(
                        source.region, source_status, self.region, status))
                    return False
                return True
        if status == "base":
            for source in self.sources:
                source_status = source.status()
                if source_status not in ["base", "idle"]:
                    App.log('Sub-source {} in "{}" state while {} in "{}" state'.format(
                        source.region, source_status, self.region, status))
                    return False
                return True
        else:  # status in ["non-incremental", "uninitialized"]:
            for source in self.sources:
                source_status = source.status()
                if source_status != status:
                    App.log('Sub-source {} in "{}" state while {} in "{}" state'.format(
                        source.region, source_status, self.region, status))
                    return False
                return True

class osmChangeSourceFilter(osmChangeSource):
    """Source made by filtering elements from another source.
    Example:
    osm_trails = osmChangeSourceFilter(
            os.path.join('Cache', 'israel-and-palestine-trails-latest.osm.pbf'),
            os.path.join('Cache', 'israel-and-palestine-trails-update.osc'),
            os.path.join('Cache', 'israel-and-palestine-trails-updated.osm.pbf'),
            "asia/israel-and-palestine-trails",
            os.path.join('Filters', 'trails_filter.txt'),
            osm_source)
    where osm_source is a osmChangeSource
    
    """
    def __init__(self, base, changes, updated, region, osmfilter, source):
        # Filter sources do not use a tempdir as there is no direct download
        # from servers
        osmChangeSource.__init__(self, base, changes, updated, ".", region)
        self.osmfilter = osmfilter
        self.source = source

    def __filter(self):
        App.log("=== Filtering latest map data into "+self.region+" ===")
        status = self.status()
        exit_code = (
                App.run_program(
                    "osmconvert.exe", 7200,
                    [self.source.updated,"-o="+self.source.updated+".o5m"]
                    + self.osmconvert_params)
                or App.run_program(
                    "osmfilter.exe", 16200, 
                    ["--parameter-file="+self.osmfilter,
                        self.source.updated+".o5m",
                        "-o="+self.updated+".o5m"]) 
                or App.run_program(
                    "osmconvert.exe", 7200,
                    [self.updated+".o5m", "-o="+self.updated]
                    + self.osmconvert_params)
                )
        if status == "base":
                exit_code = (
                    exit_code
                    or App.run_program(
                        "osmconvert.exe", 7200,
                        ["--diff", self.base, self.updated+".o5m", "-o="+self.changes]
                        + self.osmconvert_params)
                    )
        self.silent_remove(self.source.updated+".o5m")
        self.silent_remove(self.updated+".o5m")
        if exit_code:
            self.silent_remove(self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def downloadBase(self):
        App.log("=== Downloading "+self.region+" latest map data ===")
        self.silent_remove(self.base)
        self.silent_remove(self.updated)
        self.silent_remove(self.changes)
        self.silent_remove(self.changes+".old")
        return self.source.downloadBase() or self.__filter()

    def downloadChange(self):
        App.log("=== Downloading "+self.region+" map changes ===")
        status = self.status()
        if status not in ["idle", "base"]:
            App.log('Should not download changes for {} in status "{}".'.format(
                self.region, status))
            raise RuntimeError
        status = self.source.status()
        exit_code = 0
        if status not in ["incremental", "non-incremental"]:
            exit_code = (
                    self.source.downloadUpdate()
                    or self.__filter() 
                    )
        if exit_code:
            self.silent_remove(self.changes)
            self.silent_remove(self.updated)
            App.log("  Program finished with exit code {}.".format(
                exit_code))
        return exit_code

    def createUpdate(self):
        # Update creation is built into downloadChange()
        return 0

    def advance(self):
        osmChangeSource.advance(self)
        self.source.advance()

    def consistent(self):
        status = self.status()
        if status == "changes":
            App.log('Filtered {} in "{}" state'.format(
                self.region, status))
            return False
        source_status = self.source.status()
        if source_status != status:
            App.log('Source {} in "{}" state while filtered {} in "{}" state'.format(
                self.source.region, source_status, self.region, status))
            return False
        return True

# vim: set shiftwidth=4 expandtab textwidth=0:
