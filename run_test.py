#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import click
DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(DIR, ".."))
from commons import *


@click.group(name="mode")
def main():
    pass


@main.command(name="build")
def build():
    subprocess.call(["mvn", "install", "-DskipTests"], cwd=DIR)
    subprocess.call(["java", "-cp", PHOSPHOR_JAR_PATH, "edu.columbia.cs.psl.phosphor.Instrumenter",
                    "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar", "instrumented"], cwd=DIR)


@main.command(name="instrument")
def instrument():
    subprocess.call(["java", "-cp", PHOSPHOR_JAR_PATH, "edu.columbia.cs.psl.phosphor.Instrumenter",
                    "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar", "instrumented"], cwd=DIR)


@main.command(name="origin")
@click.option('--debug', default=False, help='Enable debugging.')
def origin(debug: bool):
    command = ["-cp", "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar",
               "org.apache.hadoop.hdfs.server.namenode.TestCheckpoint"]
    if debug:
        command.insert(0, "-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005")
    subprocess.call(["java"] + command)


@main.command(name="dynamic")
def dynamic():
    subprocess.call([INSTRUMENTED_JAVA_EXEC,
                     "-cp", "instrumented/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar",
                     f"-javaagent:{PHOSPHOR_AGENT_PATH}",
                     f"-javaagent:{RUNTIME_JAR_PATH}",
                     f"-agentpath:{NATIVE_LIB_PATH}=taint:Lorg/apache/hadoop/hdfs",
                     "org.apache.hadoop.hdfs.server.namenode.TestCheckpoint"])


if __name__ == '__main__':
    main()
