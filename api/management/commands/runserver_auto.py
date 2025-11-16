import socket
from contextlib import closing

from django.core.management.base import BaseCommand
from django.core.management import call_command


def port_is_free(port, host='127.0.0.1'):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind((host, int(port)))
            return True
        except OSError:
            return False


class Command(BaseCommand):
    help = 'Runserver but try the next available port if the starting port is in use.'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=int, default=8000, help='Starting port (default: 8000)')
        parser.add_argument('--end', type=int, default=8100, help='End port range (default: 8100)')
        parser.add_argument('--addr', default='127.0.0.1', help='Address to bind to')

    def handle(self, *args, **options):
        start = options['start']
        end = options['end']
        addr = options['addr']

        chosen_port = None
        for port in range(start, end + 1):
            if port_is_free(port, host=addr):
                chosen_port = port
                break

        if not chosen_port:
            raise SystemExit(f'No available ports in range {start}-{end}')

        self.stdout.write(self.style.SUCCESS(f'Starting server at {addr}:{chosen_port}'))
        call_command('runserver', f'{addr}:{chosen_port}')
