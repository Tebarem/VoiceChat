import argparse


def int_or_str(text):
	"""
	Helper function for argument parsing.
	Converts string to int if it can, otherwise returns the string
	"""
	if text.isdigit():
		return int(text)
	# else
	return text


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit'
        )

        self.args, self.remaining = self.parser.parse_known_args()

        if self.args.list_devices:
            # print(sd.query_devices())
            self.parser.exit(0)

        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[self.parser]
        )
        self.parser.add_argument(
            '-i', '--input-device', type=int_or_str,
            help='input device (numeric ID or substring)'
        )
        self.parser.add_argument(
            '-o', '--output-device', type=int_or_str,
            help='output device (numeric ID or substring)'
        )
        self.parser.add_argument(
            '-c', '--channels', type=int, default=2,
            help='number of channels'
        )
        self.parser.add_argument('--dtype', help='audio data type')
        self.parser.add_argument('--samplerate', type=float, help='sampling rate')
        self.parser.add_argument('--blocksize', type=int, help='block size')
        self.parser.add_argument('--latency', type=float, help='latency in seconds')
        self.args = self.parser.parse_args(self.remaining)
