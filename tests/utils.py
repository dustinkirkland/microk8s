import datetime
import time
import yaml
from subprocess import check_output, CalledProcessError


def run_until_success(cmd, timeout_insec=300):
    """
    Run a command untill it succeeds or times out.
    Args:
        cmd: Command to run
        timeout_insec: Time out in seconds

    Returns: The string output of the command

    """
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=timeout_insec)
    while True:
        try:
            output = check_output(cmd.split()).strip().decode('utf8')
            return output.replace('\\n', '\n')
        except CalledProcessError:
            if datetime.datetime.now() > deadline:
                raise
            print("Retrying {}".format(cmd))
            time.sleep(3)


def kubectl(cmd):
    """
    Do a kubectl <cmd>
    Args:
        cmd: left part of kubectl <left_part> command

    Returns: the kubectl response in a string

    """
    cmd = '/snap/bin/microk8s.kubectl ' + cmd
    return run_until_success(cmd)


def kubectl_get(target):
    """
    Do a kubectl get and return the results in a yaml structure.
    Args:
        target: which resource we are getting

    Returns: YAML structured response

    """
    cmd = 'get -o yaml ' + target
    output = kubectl(cmd)
    return yaml.load(output)


def wait_for_pod_state(pod, namespace, desired_state, desired_reason=None, label=None):
    """
    Wait for a a pod state. If you do not specify a pod name and you set instead a label
    only the first pod will be checked.
    """
    while True:
        cmd = 'po {} -n {}'.format(pod, namespace)
        if label:
            cmd += ' -l {}'.format(label)
        data = kubectl_get(cmd)
        if pod == "":
            status = data['items'][0]['status']
        else:
            status = data['status']
        if 'containerStatuses' in status:
            container_status = status['containerStatuses'][0]
            state, details = list(container_status['state'].items())[0]
            if desired_reason:
                reason = details.get('reason')
                if state == desired_state and reason == desired_reason:
                    break
            elif state == desired_state:
                break
        time.sleep(3)


def microk8s_enable(addon):
    """
    Disable an addon

    Args:
        addon: name of the addon

    """
    cmd = '/snap/bin/microk8s.enable {}'.format(addon)
    time.sleep(10)
    return run_until_success(cmd)


def microk8s_disable(addon):
    """
    Enable an addon

    Args:
        addon: name of the addon

    """
    cmd = '/snap/bin/microk8s.disable {}'.format(addon)
    time.sleep(10)
    return run_until_success(cmd)
