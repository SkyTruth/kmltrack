import unittest
import tempfile
import shutil
import click.testing
import os.path
import kmltrack.cli
import msgpack
import elementtree.ElementTree


class KmlTrackTest(unittest.TestCase):
    keep_tree = False

    test_track = [
        {'lat': 0.0, 'lon': 0.3, 'timestamp': '1970-01-01T00:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.1, 'lon': 0.2, 'timestamp': '1970-01-01T01:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.2, 'lon': 0.1, 'timestamp': '1970-01-01T02:00:00.000Z', 'course': 180.0, 'color': 0.5},
        {'lat': 0.3, 'lon': 0.0, 'timestamp': '1970-01-01T03:00:00.000Z', 'course': 180.0, 'color': 0.5},
        ]

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.runner = click.testing.CliRunner()
        if self.keep_tree:
            print 'KmlTrackTest is running in %s' % self.dir
        self.infile = os.path.join(self.dir, 'in.msgpack')
        with open(self.infile, 'w') as f:
            for row in self.test_track:
                msgpack.dump(row, f)
        self.outfile = os.path.join(self.dir, 'out.kml')

    def tearDown(self):
        if not self.keep_tree:
            shutil.rmtree(self.dir)

    def runcmd(self, *args):
        return self.runner.invoke(kmltrack.cli.main, args, catch_exceptions=False)

    def test_defaults(self):
        self.runcmd("--verify-rows", self.infile, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,0.0,0 0.2,0.1,0 0.1,0.2,0 0.0,0.3,0')

        points = mydoc.findall('//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(points), 4)
        self.assertEqual([point.text.strip() for point in points], ['0.3,0.0,0', '0.2,0.1,0', '0.1,0.2,0', '0.0,0.3,0'])

        timestamps = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}TimeStamp/{http://www.opengis.net/kml/2.2}when')
        self.assertEqual([timestamp.text.strip() for timestamp in timestamps], ['1970-01-01T00:00:00Z', '1970-01-01T01:00:00Z', '1970-01-01T02:00:00Z', '1970-01-01T03:00:00Z'])

        colors = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}Style//{http://www.opengis.net/kml/2.2}color')
        self.assertEqual([color.text.strip() for color in colors], ['ff7ab6fa', 'ff7ab6fa', 'ff7ab6fa', 'ff7ab6fa'])

    def test_remap(self):
        self.runcmd("--verify-rows", "--map", "color=1.0", "--map", "lat=float(lat) + 1.0", "--map", "timestamp=d(timestamp) + datetime.timedelta(1)", self.infile, self.outfile)

        mydoc = elementtree.ElementTree.ElementTree(file=self.outfile)

        lines = mydoc.findall('//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text.strip(), '0.3,1.0,0 0.2,1.1,0 0.1,1.2,0 0.0,1.3,0')

        points = mydoc.findall('//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        self.assertEqual(len(points), 4)
        self.assertEqual([point.text.strip() for point in points], ['0.3,1.0,0', '0.2,1.1,0', '0.1,1.2,0', '0.0,1.3,0'])

        timestamps = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}TimeStamp/{http://www.opengis.net/kml/2.2}when')
        self.assertEqual([timestamp.text.strip() for timestamp in timestamps], ['1970-01-02T00:00:00Z', '1970-01-02T01:00:00Z', '1970-01-02T02:00:00Z', '1970-01-02T03:00:00Z'])

        colors = mydoc.findall('//{http://www.opengis.net/kml/2.2}Placemark/{http://www.opengis.net/kml/2.2}Style//{http://www.opengis.net/kml/2.2}color')
        self.assertEqual([color.text.strip() for color in colors], ['ffe5fafd', 'ffe5fafd', 'ffe5fafd', 'ffe5fafd'])

    def test_verify(self):
        result = self.runcmd("--verify-rows", "--map", "timestamp=foo()", self.infile, self.outfile)

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error in column mapper expression: name 'foo' is not defined", result.output)
