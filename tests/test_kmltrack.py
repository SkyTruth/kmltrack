import unittest
import tempfile
import shutil
import click.testing
import os.path
import kmltrack.cli
import kmltrack.iterators
import kmltrack.template
import msgpack
import json
import csv
import elementtree.ElementTree


class KmlTrackTest(unittest.TestCase):
    keep_tree = True

    test_track = [
        {'lat': 0.0, 'lon': 0.3, 'timestamp': '1970-01-01T00:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.1, 'lon': 0.2, 'timestamp': '1970-01-01T12:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.2, 'lon': 0.1, 'timestamp': '1970-01-02T00:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.3, 'lon': 0.0, 'timestamp': '1970-01-02T12:00:00.000Z', 'course': 180.0, 'color': 0.5},
        ]

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.runner = click.testing.CliRunner()
        if self.keep_tree:
            print 'KmlTrackTest is running in %s' % self.dir
        self.infile_msgpack = os.path.join(self.dir, 'in.msgpack')
        with open(self.infile_msgpack, 'w') as f:
            for row in self.test_track:
                msgpack.dump(row, f)
 
        self.infile_json = os.path.join(self.dir, 'in.json')
        with open(self.infile_json, 'w') as f:
            for row in self.test_track:
                json.dump(row, f)
                f.write('\n')

        self.infile_csv = os.path.join(self.dir, 'in.csv')
        with open(self.infile_csv, 'w') as f:
            f = csv.DictWriter(f, fieldnames=['lat', 'lon', 'timestamp', 'course', 'color'])
            f.writeheader()
            for row in self.test_track:
                f.writerow(row)

        self.outfile = os.path.join(self.dir, 'out.kml')

    def tearDown(self):
        if not self.keep_tree:
            shutil.rmtree(self.dir)

    def runcmd(self, *args):
        return self.runner.invoke(kmltrack.cli.main, args, catch_exceptions=False)

    def test_defaults(self):
        result = self.runcmd("--verify-rows", self.infile_msgpack, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,0.0,0 0.2,0.1,0 0.1,0.2,0 0.0,0.3,0')

        points = mydoc.findall('//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(points), 4)
        self.assertEqual([point.text.strip() for point in points], ['0.3,0.0,0', '0.2,0.1,0', '0.1,0.2,0', '0.0,0.3,0'])

        timestamps = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}TimeStamp/{http://www.opengis.net/kml/2.2}when')
        self.assertEqual([timestamp.text.strip() for timestamp in timestamps], ['1970-01-01T00:00:00Z', '1970-01-01T12:00:00Z', '1970-01-02T00:00:00Z', '1970-01-02T12:00:00Z'])

        colors = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}Style//{http://www.opengis.net/kml/2.2}color')
        self.assertEqual([color.text.strip() for color in colors], ['ff7ab6fa', 'ff7ab6fa', 'ff7ab6fa', 'ff7ab6fa'])

    def test_csv(self):
        self.runcmd("--verify-rows", self.infile_csv, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,0.0,0 0.2,0.1,0 0.1,0.2,0 0.0,0.3,0')

    def test_json(self):
        self.runcmd("--verify-rows", self.infile_json, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,0.0,0 0.2,0.1,0 0.1,0.2,0 0.0,0.3,0')

    def test_remap(self):
        self.runcmd("--verify-rows", "--map", "color=1.0", "--map", "lat=float(lat) + 1.0", "--map", "timestamp=d(timestamp) + datetime.timedelta(1)", self.infile_msgpack, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,1.0,0 0.2,1.1,0 0.1,1.2,0 0.0,1.3,0')

        points = mydoc.findall('//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(points), 4)
        self.assertEqual([point.text.strip() for point in points], ['0.3,1.0,0', '0.2,1.1,0', '0.1,1.2,0', '0.0,1.3,0'])

        timestamps = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}TimeStamp/{http://www.opengis.net/kml/2.2}when')
        self.assertEqual([timestamp.text.strip() for timestamp in timestamps], ['1970-01-02T00:00:00Z', '1970-01-02T12:00:00Z', '1970-01-03T00:00:00Z', '1970-01-03T12:00:00Z'])

        colors = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}Style//{http://www.opengis.net/kml/2.2}color')
        self.assertEqual([color.text.strip() for color in colors], ['ffe5fafd', 'ffe5fafd', 'ffe5fafd', 'ffe5fafd'])

    def test_verify(self):
        result = self.runcmd("--verify-rows", "--map", "timestamp=foo()", self.infile_msgpack, self.outfile)

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error in column mapper expression: name 'foo' is not defined", result.output)

    def test_dont_verify(self):
        result = self.runcmd("--verbose", "--map", "timestamp=foo()", self.infile_msgpack, self.outfile)
        self.assertEqual(result.exit_code, 0)
        
        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)
        points = mydoc.findall('//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(points), 0)

    def test_lookahead(self):
        self.assertFalse(hasattr(kmltrack.iterators.lookahead(iter([])), "peek"))

        with self.assertRaises(StopIteration):
            kmltrack.iterators.lookahead(iter([])).next()

        l = kmltrack.iterators.lookahead(iter([1, 2]))
        self.assertEqual(l.peek, 1)
        self.assertEqual(l.next(), 1)
        self.assertEqual(l.peek, 2)
        self.assertEqual(l.next(), 2)
        with self.assertRaises(StopIteration):
            l.next()

    def test_template(self):
        class TestTemplate(kmltrack.template.Template):
            template = "$$ A ${foo} B $bar C $fie D"
            foo = "hello"
            def bar(self, f, ctx):
                f.write("world")

            class fie(kmltrack.template.Template):
                template = "( $nana )"
                nana = "better"

        outfile = os.path.join(self.dir, 'out.tmpl')
        with open(outfile, 'w') as f:
            TestTemplate(f)

        with open(outfile) as f:
            out = f.read()

        self.assertIn("hello", out)
        self.assertIn("world", out)
        self.assertIn("better", out)
 
