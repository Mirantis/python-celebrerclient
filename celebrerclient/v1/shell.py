from celebrerclient.common import utils


def do_list_services(ic, args):
    """Get services list"""
    result = ic.actions.list_services()
    columns = ['Name']
    utils.print_list(result, columns)


def do_list_reports(ic, args):
    """Get reports list"""
    result = ic.actions.list_reports()
    columns = ['Name']
    utils.print_list(result, columns)


@utils.arg("report_id", metavar='<REPORT_ID>', help='Report ID')
def do_show_report(ic, args):
    """Get detail information about report"""
    result = ic.actions.list_services(args.report_id)
    columns = ['Name']
    utils.print_list(result, columns)


@utils.arg('services', metavar="service-1,service-2,service-3", action='append',
           default=[], help='Services list')
def do_run_services(ic, args):
    """Run service under coverage"""
    action_id = ic.actions.run_services(arguments={
        'action': args.action,
        'object_id': args.object,
        'args': {
            arg.split('=')[0]: arg.split('=')[1] for arg in args.args
        }
    })
    print action_id


@utils.arg("report_id", metavar='<REPORT_ID>', help='Report ID')
def do_download_report(ic, args):
    """Get detail information about report"""
    result = ic.actions.download_reports(args.report_id)
    columns = ['Name']
    utils.print_list(result, columns)
