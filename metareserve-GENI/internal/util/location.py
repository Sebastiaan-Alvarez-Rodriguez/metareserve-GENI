# This file contains all relevant paths for MetaSpark to function
# Here, we chose for a function-call approach instead of
# a global object, as we don't have to maintain state here.

import util.fs as fs
from config.meta import cfg_meta_instance as metacfg
from remote.util.deploymode import DeployMode

#################### MetaSpark directories ####################
def get_metaspark_cluster_conf_dir():
    return fs.join(get_metaspark_conf_dir(), 'cluster')

def get_metaspark_conf_dir():
    return fs.join(fs.abspath(), 'conf')

def get_metaspark_dep_dir():
    return fs.join(fs.abspath(), 'deps')

def get_metaspark_data_dir():
    return fs.join(fs.abspath(), 'data')

def get_metaspark_experiments_dir():
    return fs.join(fs.abspath(), 'experiments')

def get_metaspark_graphs_dir():
    return fs.join(fs.abspath(), 'graphs')

def get_metaspark_keys_dir():
    return fs.join(fs.abspath(), 'keys')

def get_metaspark_log4j_conf_dir():
    return fs.join(get_metaspark_conf_dir(), 'log4j')

def get_metaspark_jar_dir():
    return fs.join(fs.abspath(), 'jars')

def get_metaspark_logs_dir():
    return fs.join(fs.abspath(), 'logs')

def get_metaspark_results_dir():
    return fs.join(fs.abspath(), 'results')

def get_metaspark_recordings_dir():
    return fs.join(fs.abspath(), 'recordings')

def get_metaspark_reservations_dir():
    return fs.join(fs.abspath(), 'reservations')

def get_metaspark_ceph_dir():
    return fs.join(get_metaspark_reservations_dir(), 'ceph')

#################### Spark directories ####################
def get_spark_dir():
    return fs.join(get_metaspark_dep_dir(), 'spark')

def get_spark_bin_dir():
    return fs.join(get_spark_dir(), 'bin')

def get_spark_sbin_dir():
    return fs.join(get_spark_dir(), 'sbin')

def get_spark_conf_dir():
    return fs.join(get_spark_dir(), 'conf')

def get_spark_logs_dir():
    return fs.join(get_spark_dir(), 'logs')

def get_spark_work_dir(deploymode):
    if deploymode == DeployMode.STANDARD:
        return fs.join(get_spark_dir(), 'work')
    elif deploymode == DeployMode.LOCAL:
        return fs.join(get_node_local_dir(), 'work')
    elif deploymode == DeployMode.LOCAL_SSD:
        return fs.join(get_node_local_ssd_dir(), 'work')
    elif deploymode == DeployMode.RAM:
        return fs.join(get_node_ram_dir(), 'work')
    else:
        raise RuntimeError('Could not find a workdir destination for deploymode: {}'.format(deploymode))

#################### Remote directories ####################
def get_remote_metaspark_parent_dir(sshconfig=None):
    return metacfg.ssh.remote_metaspark_dir if sshconfig == None else sshconfig.remote_metaspark_dir

def get_remote_metaspark_dir(sshconfig=None):
    return fs.join(get_remote_metaspark_parent_dir(sshconfig), fs.basename(fs.abspath()))

def get_remote_metaspark_conf_dir():
    return fs.join(get_remote_metaspark_dir(), 'conf')

def get_remote_metaspark_data_dir():
    return fs.join(get_remote_metaspark_dir(), 'data')

def get_remote_metaspark_jar_dir():
    return fs.join(get_remote_metaspark_dir(), 'jars')

def get_remote_metaspark_logs_dir(sshconfig=None):
    return fs.join(get_remote_metaspark_dir(sshconfig), 'logs')

#################### Node directories ####################

def get_node_local_dir():
    return '/local/{}/'.format(metacfg.ssh.ssh_user_name)

def get_node_local_ssd_dir():
    return '/local-ssd/{}/'.format(metacfg.ssh.ssh_user_name)

def get_node_ram_dir():
    return '/dev/shm/{}/'.format(metacfg.ssh.ssh_user_name)


# Returns path containing links to the dataset for each deploymode
def get_node_data_link_dir(deploymode):
    if deploymode == DeployMode.STANDARD:
        return fs.dirname(get_metaspark_data_dir(), 'data_link')
    elif deploymode == DeployMode.LOCAL:
        return fs.join(get_node_local_dir(), 'data_link')
    elif deploymode == DeployMode.LOCAL_SSD:
        return fs.join(get_node_local_ssd_dir(), 'data_link')
    else:
        raise RuntimeError('Could not find a data-linkdir destination for deploymode: {}'.format(deploymode))


# Directory path containing the datasets for each deploymode
def get_node_data_dir(deploymode):
    if deploymode == DeployMode.STANDARD:
        return get_metaspark_data_dir()
    elif deploymode == DeployMode.LOCAL:
        return fs.join(get_node_local_dir(), 'data')
    elif deploymode == DeployMode.LOCAL_SSD:
        return fs.join(get_node_local_ssd_dir(), 'data')
    elif deploymode == DeployMode.RAM:
        return fs.join(get_node_ram_dir(), 'data')
    else:
        raise RuntimeError('Could not find a datadir destination for deploymode: {}'.format(deploymode))
