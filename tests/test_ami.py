import logging

import pytest

log = logging.getLogger('spel_validation')
log.setLevel(logging.INFO)


@pytest.mark.hvm
def test_10_gigabit(host):
    interface = host.interface('eth0')
    assert interface.speed == 10000


def test_root_volume_is_resized(host):
    cmd = 'test $(vgs --noheadings -o pv_free | sed \'s/ //g\') != 0'
    pv_free = host.run(cmd)
    assert pv_free.exit_status == 0


@pytest.mark.parametrize("name", [
    ("aws-amitools-ec2"),
    ("aws-apitools-as"),
    ("aws-apitools-cfn"),
    ("aws-apitools-common"),
    ("aws-apitools-ec2"),
    ("aws-apitools-elb"),
    ("aws-apitools-iam"),
    ("aws-apitools-mon"),
    ("aws-apitools-rds"),
    ("aws-cfn-bootstrap")
])
def test_common_aws_pkgs(host, name):
    pkg = host.package(name)
    if pkg.is_installed:
        log.info(
            '%s',
            {'pkg': pkg.name, 'version': pkg.version, 'release': pkg.release})
    assert pkg.is_installed


@pytest.mark.el7
@pytest.mark.parametrize("name", [
    ("aws-scripts-ses")
])
def test_el7_aws_pkgs(host, name):
    pkg = host.package(name)
    if pkg.is_installed:
        log.info(
            '%s',
            {'pkg': pkg.name, 'version': pkg.version, 'release': pkg.release})
    assert pkg.is_installed


def test_aws_cli_is_in_path(host):
    cmd = 'aws --version'
    aws = host.run(cmd)
    log.info('\n%s', aws.stderr)
    assert host.exists('aws')


def test_repo_access(host):
    cmd = 'yum repolist all 2> /dev/null | sed -n \'/^repo id/,$p\''
    repos = host.run(cmd)
    log.info('stdout:\n%s', repos.stdout)
    log.info('stderr:\n%s', repos.stderr)
    assert repos.exit_status == 0


def test_boot_is_mounted(host):
    boot = host.mount_point('/boot')
    assert boot.exists


def test_tmp_mount_properties(host):
    tmp = host.mount_point('/tmp')
    assert tmp.exists
    assert tmp.device == 'tmpfs'
    assert tmp.filesystem == 'tmpfs'


@pytest.mark.el7
def test_el7_selinux_enforcing(host):
    cmd = 'test $(getenforce) = \'Enforcing\''
    selinux_permissive = host.run(cmd)
    assert selinux_permissive.exit_status == 0


@pytest.mark.el7
@pytest.mark.fips_enabled
def test_el7_fips_enabled(host):
    fips = host.file('/proc/sys/crypto/fips_enabled')
    assert fips.exists and fips.content.strip() == b'1'


@pytest.mark.el7
@pytest.mark.fips_disabled
def test_el7_fips_disabled(host):
    fips = host.file('/proc/sys/crypto/fips_enabled')
    assert not fips.exists or fips.content.strip() == b'0'


@pytest.mark.parametrize("names", [
    ([
        'python3',
        'python36',
    ])
])
def test_python3_installed(host, names):
    pkg = type('pkg', (object,), {'is_installed': False})
    for name in names:
        pkg = host.package(name)
        if pkg.is_installed:
            break

    assert pkg.is_installed
    log.info(
        '%s',
        {'pkg': pkg.name, 'version': pkg.version, 'release': pkg.release})


@pytest.mark.el7
@pytest.mark.parametrize("realpath,link", [
    ('/usr/bin/python3.6', '/usr/bin/python3')
])
def test_python3_symlink(host, realpath, link):
    python3_symlink = host.file(link).linked_to
    assert python3_symlink == realpath


@pytest.mark.parametrize("version", [
    (b'3.6')
])
def test_python3_version(host, version):
    cmd = 'python3 --version'
    python3_version = host.run(cmd)
    log.info('`%s` stdout: %s', cmd, python3_version.stdout)
    log.info('`%s` stderr: %s', cmd, python3_version.stderr)

    assert python3_version.exit_status == 0

    # Example stdout content: b'Python 3.6.8'
    assert python3_version.stdout.strip().split()[1].startswith(version)


@pytest.mark.el7
def test_timedatectl_dbus_status(host):
    cmd = 'timedatectl'
    timedatectl = host.run(cmd)
    log.info('stdout:\n%s', timedatectl.stdout)
    log.info('stderr:\n%s', timedatectl.stderr)
    assert timedatectl.exit_status == 0


@pytest.mark.el7
def test_var_run_symlink(host):
    var_run_symlink = host.file('/var/run').linked_to
    assert var_run_symlink == '/run'


@pytest.mark.parametrize("service", [
    ("autotune.service"),
    ("amazon-ssm-agent.service"),
    ("hibinit-agent.service"),
    ("ec2-instance-connect.service")
])

def test_systemd_services(host, service):
    chk_service = host.service(service)
    assert chk_service.is_enabled
