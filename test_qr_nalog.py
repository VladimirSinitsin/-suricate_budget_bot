from nalog_python import NalogRuPython

import json

client = NalogRuPython()
qr_code = "t=20200709T2008&s=7273.00&fn=9282440300688488&i=14186&fp=1460060363&n=1"
ticket = client.get_ticket(qr_code)
print(json.dumps(ticket, indent=4, ensure_ascii=False))
