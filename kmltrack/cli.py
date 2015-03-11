import sys
import traceback
import kmltrack.fileconverter
import click


def key_val_parser(ctx, param, value):
    return {val.split('=')[0]: val.split('=')[1]
            for val in value}


@click.command()
@click.option('--verbose', default=False, is_flag=True, help='More verbose error messages')
@click.option('--verify-rows', default=False, is_flag=True, help='Verify rows and break if a bad row is detected')
@click.option('--format', default=None, help='Input format. Valid values: msgpack, json, csv')
@click.option(
    '--map', metavar='FIELD=EXPR', multiple=True, callback=key_val_parser,
    help="""Calculate values for the various columns. EXPR is any python expression over the row column values available as variables.

Defaults:
    --map lat=float(lat)
    --map lon=float(lat)
    --map timestamp=d(timestamp)
    --map course=float(course)
    --map color=float(color)

    Color should be either a float in the range [0.0, 1.0] or a hex string 'AABBGGRR'
"""
)
@click.argument('input')
@click.argument('output')
def main(verbose, verify_rows, format, map, input, output):
    try:
        if format is None and '.' in input:
            format = input.split('.')[-1]

        converter = getattr(kmltrack.fileconverter, "%s_to_kml" % (format,))

        converter(input, output, verbose=verbose, verify_rows=verify_rows, format=format, column_map=map)
    except Exception, e:
        if verbose:
            traceback.print_exc()
        raise click.UsageError(str(e))
