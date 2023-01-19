# -*- coding: utf-8 -*-
# ############################################################################
#
#    Copyright Eezee-It (C) 2016
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import glob
import logging
import os
import shutil
from os.path import basename, normpath

import colorama
from invoke import task

colorama.init()
LOG_COLORS = {
    logging.ERROR: colorama.Fore.RED,
    logging.WARNING: colorama.Fore.YELLOW,
    logging.INFO: colorama.Fore.GREEN,
    logging.DEBUG: colorama.Fore.MAGENTA,
}


class ColorFormatter(logging.Formatter):
    def __init__(self, format="%(message)s"):
        """Create a new formatter that adds colors"""
        super(ColorFormatter, self).__init__(format)

    def format(self, record, *args, **kwargs):
        if record.levelno in LOG_COLORS:
            record.msg = LOG_COLORS[record.levelno] \
                + record.msg + colorama.Style.RESET_ALL
        return super(ColorFormatter, self).format(record, *args, **kwargs)


# Logging
log = logging.getLogger('tasks')
_output = logging.StreamHandler()
_output.setFormatter(ColorFormatter())
log.addHandler(_output)
log.setLevel(logging.DEBUG)


###########################################################
# Database commands


def _pg_run(c, cmd, **kw):
    if c.get('pg_user'):
        cmd = 'sudo -u %s %s' % (c.pg_user, cmd)
    return c.run(cmd, **kw)


def _get_database_name(c, database_name=''):
    return database_name or c.database_name


@task
def drop_db(c, database_name=''):
    """Remove the database"""
    database_name = _get_database_name(c, database_name)
    log.info('• Dropping Database %s' % database_name)
    _pg_run(c, "dropdb %s --if-exists" % database_name)


@task
def start_postgres(c):
    """Start postgresql service"""
    c.run("sudo service postgresql start")


@task
def list_db(c):
    """List databases"""
    log.info('• List Databases')
    _pg_run(c, "psql -l")


@task
def create_db(c, database_name='', template='', dump_file='', reset_password=True):
    """Create a database for Odoo (empty or from dump)"""
    database_name = _get_database_name(c, database_name)
    if dump_file:
        drop_db(c, database_name)
    log.info('• Create database %s' % database_name)
    cmd = ['createdb']
    owner = c.get('database_owner')
    if owner:
        cmd += ['--owner', owner]
    if template:
        cmd += ['--template=' + template]
    cmd.append(database_name)
    _pg_run(c, ' '.join(cmd))
    if dump_file:
        log.info('• Import dump file: %s' % dump_file)
        cmd = ['psql', database_name]
        pg_user = c.get('pg_user', '')
        if owner and owner != pg_user:
            cmd += ['-U', owner, '--host', 'localhost']
        cmd.extend(['<', dump_file])
        _pg_run(c, ' '.join(cmd), pty=True)
        if reset_password:
            reset_passwords(c, database_name)


@task
def reset_passwords(c, database_name='', password='admin'):
    """Reset Odoo password for all users"""
    log.info('• Resetting password for all users')
    from passlib.context import CryptContext
    crypt = CryptContext(schemes=['pbkdf2_sha512'])
    encrypted = crypt.encrypt('admin')
    database_name = _get_database_name(c, database_name)
    query = "update res_users set password='%s'" % encrypted
    _pg_run(c, "psql %s -c '%s'" % (database_name, query.replace("'", "'\\''")))


###########################################################
# Linting


@task
def lint_flake8(c, addons=''):
    """Run flake8"""
    log.info('• Flake8')
    paths = ['.']

    if addons:
        paths = _find_addons_path(c, addons.split(','))

    flakerc = '.flake8'
    for path in paths:
        command = "flake8 %s --config=%s" % (path, flakerc)
        c.run(command)


@task
def lint_odoo_lint(c, addons=''):
    """Run pylint"""
    log.info('• pyLinter')

    if addons:
        addons = _find_addons_path(c, addons.split(','))
    else:
        addons = _find_addons_path(c, _get_odoo_addons(c))

    command = "pylint --errors-only --load-plugins=pylint_odoo -d all -e odoolint" + \
        " %s --disable=%s "

    if c.debug:
        log.debug('Addon list')
        log.debug(str(addons))

    for addon in addons:
        addon_name = basename(normpath(addon))
        log.debug("Pylint check addon: %s" % addon_name)
        c.run(command % (addon, c.odoo_lint_disable))


@task
def lint_xml(c, addons=''):
    """Run xmllint"""
    log.info('• XML Linter')
    if os.name == 'nt':
        log.warning('Skip test on Windows')
        return
    c.run('find . -maxdepth 4 -type f -iname "*.xml" '
          '| xargs -I \'{}\' xmllint -noout \'{}\'')


@task
def lint(c, addons=''):
    """Run static code checks"""
    lint_xml(c, addons)
    lint_flake8(c, addons)
    lint_odoo_lint(c, addons)


###########################################################
# Addons


def get_project_base(c):
    """Get Odoo projet directory"""
    return os.getcwd()


def _get_odoo_addons(c, join=False):
    """List of available custom modules"""
    addons = []

    for directory in _get_addons_paths(c, include_odoo=False):
        if c.debug:
            log.debug("Directory to fetch Odoo addons: %s" % directory)
        addons += _get_addons_from_directory(directory)

    if c.custom_addons:
        _find_addons_path(c, c.custom_addons)
        addons += c.custom_addons

    if isinstance(join, str):
        addons = join.join(addons)
    return addons


def _get_addons_from_directory(directory):
    return [
        f[len(directory) + 1:].split('/')[0]
        for f in glob.glob(directory + "/*/__manifest__.py")
    ]


def _get_addons_paths(c, include_odoo=True):
    addons_path = []

    base_dir = get_project_base(c)

    for addon_directory in (c.odoo_addons_directories if include_odoo else []) or []:
        addons_path.append(os.path.join(base_dir, addon_directory))

    for addon_directory in c.custom_addons_directories or []:
        addons_path.append(os.path.join(base_dir, addon_directory))

    return addons_path


def _find_addons_path(c, addons):
    """Find the paths for the addons"""
    addons_path = []
    directories = _get_addons_paths(c)

    for addon in addons:
        found = False
        for directory in directories:
            path = os.path.join(directory, addon)
            if os.path.exists(os.path.join(path, '__manifest__.py')):
                addons_path.append(path)
                found = True
        if not found:
            raise Exception("Module %s not found!" % addon)
    return addons_path


@task()
def show_addons(c):
    """Show availabe addons"""
    addons = _get_odoo_addons(c)

    for addon in sorted(addons):
        log.debug(addon)


@task()
def show_addons_directories(c):
    """Show addon directories"""
    for attr in ['odoo_addons_directories', 'custom_addons_directories']:
        val = c.get(attr)
        if isinstance(val, list):
            log.debug('%s', attr)
            for m in val:
                log.debug('- %s', m)


###########################################################
# Running Odoo


def _get_log_handler_command_args(c):
    log_handlers = c.test_log_handlers.split(",")
    return ["--log-handler=%s " % handler for handler in log_handlers]


def _get_odoo_base_command(c, database_name='', load_languages=True, tool='', log_handler=False):
    command = [os.path.join(c.odoo_bin_directory, 'odoo-bin')]
    if tool:
        command.append(tool)
    if os.path.isfile(c.odoo_conf):
        command.extend(['-c', c.odoo_conf])
    else:
        log.debug("Use no Odoo configuration parameter")

    addons = ','.join(_get_addons_paths(c))
    command.append('--addons-path=' + addons)
    if c.debug:
        log.debug("Addons path: " + addons)

    if load_languages and c.odoo_languages:
        command.append('--load-language=%s' % (",".join(c.odoo_languages)))
        if c.debug:
            log.debug("Lang to install:")
            log.debug(",".join(c.odoo_languages))

    db = _get_database_name(c, database_name)
    command.extend(['-d', db, '--db-filter', db])

    if log_handler:
        command.extend(_get_log_handler_command_args(c))

    odoo_base_command = " ".join(command)
    if c.debug:
        log.debug("Odoo base command")
        log.debug(odoo_base_command)
    return odoo_base_command


@task()
def local_init(c, database_name='', update=False, addons='', log_errors=False):
    """Initialize a local database"""
    log.info('• Preparing Odoo')
    command = _get_odoo_base_command(c, database_name)
    if log_errors:
        command += ' --log-level=error --log-handler=odoo.modules.loading:INFO'
    command += ' --stop-after-init --workers=0 --smtp=nosmtp '
    if not addons:
        addons = _get_odoo_addons(c, join=',')
    command += ('-u' if update else '-i') + ' ' + addons
    c.run(command)


@task()
def local_run(
    c, database_name='',
    dev=None, load_languages=False, shell=False, debug=False,
):
    """Run odoo from a local database"""
    args = {}
    tool = None
    if shell:
        tool = 'shell'
        args['pty'] = True
    command = _get_odoo_base_command(
        c, database_name,
        load_languages=load_languages,
        tool=tool,
    )
    if dev:
        command += ' --dev ' + dev
    if debug:
        debug_port = c.get('debug_port') or 41234
        command = 'python -m debugpy --listen %d %s --limit-time-real 100000' % (
            debug_port, command,
        )
    c.run(command, **args)


###########################################################
# Unit tests task(s)


@task(aliases=['unittest'])
def unit_test(c, with_coverage=False, addons='', build=False, database_name=''):
    """Launch unit tests"""
    log.info('• Unittest')

    if not addons:
        addons = _get_odoo_addons(c, join=',')

    if not with_coverage:
        with_coverage = c.with_coverage

    if build:
        clean(c, database_name)
        local_init(c, database_name, addons=addons, log_errors=True)

    log.info('• Launch test(s)')

    command = _unittest_odoo_command(c, addons, database_name)

    if with_coverage:
        c.run('coverage run ' + command)
        c.run('coverage html')
        c.run('coverage report -i')
    else:
        c.run(command)


@task()
def test(c, with_coverage=False, addons='', build=False, database_name=''):
    """Static code analysis and tests"""
    lint(c, addons)
    unit_test(c, with_coverage, addons, build, database_name)


def _unittest_odoo_command(c, addons, database_name):
    command = _get_odoo_base_command(c, database_name, log_handler=True)
    command += " --test-enable --log-level=%s" % c.test_log_level
    command += " --workers=0 --smtp=nosmtp"
    command += " --stop-after-init -u %s" % addons

    if c.debug:
        log.debug("Unittest Command")
        log.debug(command)
    return command


###########################################################
# Generic and clean-up


@task
def clean(c, database_name=''):
    """Remove the database and generated files"""
    drop_db(c, database_name)

    log.info('• Cleaning coverage data')
    if os.path.exists('.coverage'):
        os.remove('.coverage')

    if os.path.exists('htmlcov'):
        shutil.rmtree('htmlcov')


@task
def github_clean(c):
    """Remove deleted branches from github"""
    # fetch and prune branches
    for remote in ['origin', 'github']:
        c.run("git fetch --prune {remote}".format(remote=remote))
    branch_output = c.run('git branch -a', hide=True)
    branches = {}
    for line in branch_output.stdout.splitlines():
        branch = line.split('/', maxsplit=2)
        if not branch[0] == '  remotes':
            continue
        remote = branches.get(branch[1])
        if not remote:
            remote = set()
            branches[branch[1]] = remote
        remote.add(branch[2])
    if 'github' not in branches or 'origin' not in branches:
        raise Exception('No branches found on remote')
    branches_to_remove = branches['github'] - branches['origin']
    for branch in branches_to_remove:
        c.run("git push github --delete '{branch}'".format(branch=branch))
    log.info('Removed %d branches from github', len(branches_to_remove))
