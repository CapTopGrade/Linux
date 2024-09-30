Project Objective:

The objective of this project is to create a daemon (system process running in the background) for automatically performing regular backups of data from one directory to another. The task involves the following steps:

    Configuration Setup: Develop a configuration file where the source directory, backup directory, backup frequency, and other parameters can be specified.
    Daemon Creation: Write C++ code for the daemon that will perform the following tasks:
        Read the configuration from the configuration file.
        Wait in the background for the next backup time.
        Create backup copies of files from the source directory to the backup directory with timestamp added.
        Log the execution of operations in the system log.
    System Integration: Integrate the daemon into the system to run at the operating system startup and regularly perform backups according to the settings.
