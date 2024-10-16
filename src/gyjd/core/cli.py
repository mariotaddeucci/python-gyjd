import argparse
import json
from collections.abc import Callable

from gyjd.core.logger import GYJDLogger
from gyjd.core.simple_injector import inject_dependencies


class CLI:
    __instance = None

    @inject_dependencies
    def __init__(self, logger: GYJDLogger = None):
        self.commands: dict[str, Callable] = {"help": self.help}
        self.logger = logger

    def help(self):
        print("Available commands and their arguments:")

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def registry(cls, func, name):
        instance = cls.get_instance()

        if name in instance.commands:
            raise ValueError(f"Command {name} already registered")

        instance.logger.debug(f"Registering {func} with command {name}")
        instance.commands.update({name: func})

    @classmethod
    def executor(cls):
        cli = cls.get_instance()

        parser = argparse.ArgumentParser(description="CLI Executor")
        parser.add_argument(
            "command",
            type=str,
            help="Command to execute",
            default="help",
            choices=list(cli.commands.keys()),
        )
        parser.add_argument("--json", type=str, help="Arguments in JSON format")

        args, unknown = parser.parse_known_args()

        kwargs = {}
        for i in range(0, len(unknown), 2):
            key = unknown[i].lstrip("--")
            value = unknown[i + 1]
            kwargs[key] = value

        if kwargs and args.json:
            cli.logger.error("Only one of JSON or key-value arguments can be passed")
            return

        if args.json:
            kwargs = json.loads(args.json)

        fn = cli.commands.get(args.command)
        if fn is None:
            cli.logger.error(f"Command {args.command} not found")
            return

        fn(**kwargs)
