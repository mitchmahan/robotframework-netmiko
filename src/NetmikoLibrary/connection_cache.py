from robot.utils import ConnectionCache


class NetmikoConnectionCache(ConnectionCache):
    """Connection handling and context switching for NetmikoLib

    This allows us to store and retrieve multiple Netmiko connections
    for use inside RobotFramework.
    """
    def __init__(self):
        ConnectionCache.__init__(self, no_current_msg='No open connection.')

    @property
    def connections(self):
        return self._connections

    @property
    def aliases(self):
        return self._aliases

    def close_current(self):
        """Close the current connection by calling netmiko.disconnect()"""
        connection = self.current
        connection.disconnect()
        if connection.config.alias is not None:
            self.aliases.pop(connection.config.alias)
        idx = connection.config.index - 1
        self.connections[idx] = self.current = self._no_current

    def close_all(self):
        """Close all open connections

        Calls .disconnect() on all netmiko connection objects stored.
        """
        return super().close_all('disconnect')

    def get_connection(self, alias_or_index=None):
        """Get a stored connection using the index or alias of the connection."""
        connection = super().get_connection(alias_or_index)
        if not connection:
            raise RuntimeError(f"Non-existing index or alias {alias_or_index}")
        return connection
