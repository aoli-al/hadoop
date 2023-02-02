#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import click
DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(DIR, ".."))
from commons import *

JAR_NAME = "hadoop-aws-3.4.0-SNAPSHOT-test-jar-with-dependencies.jar"
ORIGIN_JAR_PATH = "hadoop-tools/hadoop-aws/target"
TEST_CLASS = "org.apache.hadoop.fs.s3a.TestS3AInputStreamRetry"

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
                     f"{ORIGIN_JAR_PATH}/{JAR_NAME}", "instrumented"], cwd=DIR)


@main.command(name="origin")
@click.option('--debug', default=False, help='Enable debugging.')
def origin(debug: bool):
    command = ["-cp", f"{ORIGIN_JAR_PATH}/{JAR_NAME}", TEST_CLASS]
    if debug:
        command.insert(0, "-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005")
    subprocess.call(["java"] + command)

@main.command(name="static")
def static():
    subprocess.call(["java",
                     "-cp",
                     f"{ORIGIN_JAR_PATH}/{JAR_NAME}",
                     f"-javaagent:{RUNTIME_JAR_PATH}=static:{INSTRUMENTATION_CLASSPATH}",
                     f"-agentpath:{NATIVE_LIB_PATH}=exchain:Lorg/apache/hadoop/hdfs",
                     TEST_CLASS])
    args = ["./gradlew", "static-analyzer:run", f"--args={ORIGIN_CLASSPATH} {DIR}/static-results"]
    print(args)
    subprocess.call(args, cwd=os.path.join(DIR, "../.."))


@main.command(name="dynamic")
def dynamic():
    subprocess.call([INSTRUMENTED_JAVA_EXEC,
                     "-cp", f"instrumented/{JAR_NAME}",
                     f"-javaagent:{PHOSPHOR_AGENT_PATH}",
                     f"-javaagent:{RUNTIME_JAR_PATH}=dynamic:{INSTRUMENTATION_CLASSPATH}",
                     f"-agentpath:{NATIVE_LIB_PATH}=exchain:Lorg/apache/hadoop/fs",
                     TEST_CLASS])


if __name__ == '__main__':
    main()
