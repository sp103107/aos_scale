# Debian Serial Permissions

Add the operator to the distribution's serial-device group (commonly `dialout`) and re-login. Confirm the actual `/dev/ttyACM*` or `/dev/ttyUSB*` device and do not grant blanket world-writable permissions.
