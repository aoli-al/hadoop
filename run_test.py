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


@main.command(name="instrument")
def instrument():
    subprocess.call(["java",
                     f"-DPhosphor.INSTRUMENTATION_CLASSPATH={INSTRUMENTATION_CLASSPATH}",
                     f"-DPhosphor.ORIGIN_CLASSPATH={ORIGIN_CLASSPATH}",
                     "-cp", PHOSPHOR_JAR_PATH, "edu.columbia.cs.psl.phosphor.Instrumenter",
                    "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar", "instrumented"], cwd=DIR)


@main.command(name="origin")
@click.option('--debug', default=False, help='Enable debugging.')
def origin(debug: bool):
    command = ["-cp", "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar",
               "org.apache.hadoop.hdfs.server.namenode.TestCheckpoint"]
    if debug:
        command.insert(0, "-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005")
    subprocess.call(["java"] + command)

@main.command(name="static")
def static():
    subprocess.call(["java",
                     "-cp",
                     "hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar",
                     f"-javaagent:{RUNTIME_JAR_PATH}=static:{INSTRUMENTATION_CLASSPATH}",
                     f"-agentpath:{NATIVE_LIB_PATH}=exchain:Lorg/apache/hadoop/hdfs",
                     "org.apache.hadoop.hdfs.server.namenode.TestCheckpoint"])
    args = ["./gradlew", "static-analyzer:run", f"--args={ORIGIN_CLASSPATH} {DIR}/static-results {ORIGIN_CLASSPATH}"]
    print(args)
    subprocess.call(args, cwd=os.path.join(DIR, "../.."))


@main.command(name="dynamic")
def dynamic():
    subprocess.call([INSTRUMENTED_JAVA_EXEC,
                     "-cp", "instrumented/hadoop-hdfs-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar",
                     f"-javaagent:{PHOSPHOR_AGENT_PATH}",
                     f"-javaagent:{RUNTIME_JAR_PATH}=dynamic:{INSTRUMENTATION_CLASSPATH}",
                     f"-agentpath:{NATIVE_LIB_PATH}=exchain:Lorg/apache/hadoop/hdfs",
                     "org.apache.hadoop.hdfs.server.namenode.TestCheckpoint"])


if __name__ == '__main__':
    main()
