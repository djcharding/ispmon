import subprocess, json, os, pytz, requests
from datetime import datetime, timedelta
from numpy import mean


SETTINGS = {
    'expected': {
        'hi': .8,
        'low': .7 # .x/x% of advertised speed that is considered normal
    },
    'purchased': {
        'upload': 15,  # purchased/advertised upload speed
        'download': 75  # purchased/advertised download speed
    },
    'to': [f'os.getenv("RECIPIENT_EMAIL")'], # the ISP's email address
    'from': f"{os.getenv('MAILGUN_FROM_NAME')} <{os.getenv('MAILGUN_FROM_EMAIL')}>",
    'data': 'data/', # location of results/ data directory
    'service_ticket': '3207895', #ticket from the ISP regarding the open case
    'date_opened': "03-25-2020" # date the ticket was opened
}

def log(message: str):
    print(message)

def send_result(result: dict):
    sender =  SETTINGS['from']
    receiver = SETTINGS['to']

    subject = f'Re: Service Ticket {SETTINGS["service_ticket"]}'

    days = calculate_days()

    message = f"""\
        
Dear Cable Bahamas,

Please note the following is related to service ticket: {SETTINGS['service_ticket']} which was opened on Wed, 25th April 2020 ({days} days ago).

In an effort to assist you with keeping accurate information regarding the current defficiencies in service relating to my subscribed REVON internet service, I've scheduled this hourly report to email your team of the ongoing performance of my service. This report consists of speetest results (using to CBL's Ookla speettest server).

I hope this will assist you as you work to resolve the issue in a timely manner.

I've also added the code used to perform this test to my GitHub so you may assess its validity.

-------------------------------------------------------------------------------------------  
    Speed summary
-------------------------------------------------------------------------------------------

    Date: {result['timestamp']}

    Client Information:

        IP: {result['ip']}
        Ticket #: {SETTINGS['service_ticket']}

    Advertised/Purchased

        Download: {SETTINGS['purchased']['download']} Mbps
        Upload: {SETTINGS['purchased']['upload']} Mbps

    Reasonable Expectation - based on 70% - from CB FAQ on speed testing.

        Download: {result['expected']['download']} Mbps
        Upload: {result['expected']['upload']} Mbps

    Actual (Current)

        Download: {result['download']} Mbps
        Upload: {result['upload']} Mbps
        Ping: {result['ping']} ms

        Speedtest image: {result['share']}


    Difference - expectation vs. actual

        Download: {floatfmt(result['download'] - result['expected']['download'])} Mbps
        Download % of expectation: {floatfmt(result['download']/result['expected']['download']) * 100}%

        Upload: {floatfmt(result['upload'] - result['expected']['upload'])} Mbps
        Upload % of expectation: {floatfmt(result['upload']/result['expected']['upload']) * 100}%

    Difference - advertised vs. actual

        Download: {floatfmt(result['download'] - SETTINGS['purchased']['download'])} Mbps 
        Download % of advertised: {floatfmt(result['download']/SETTINGS['purchased']['download']) * 100}%

        Upload: {floatfmt(result['upload'] - SETTINGS['purchased']['upload'])} Mbps
        Upload % of advertised: {floatfmt(result['upload']/SETTINGS['purchased']['upload']) * 100}%


    Average Performance

        Download: {result['average']['download']} Mbps
        Download % of resonable expectation: {floatfmt(result['average']['download'] / result['expected']['download']) * 100}%
        Download % of advertised: {floatfmt(result['average']['download'] / SETTINGS['purchased']['download']) * 100}%

        Upload: {result['average']['upload']} Mbps
        Upload % of resonable expectation: {floatfmt(result['average']['upload'] / result['expected']['upload']) * 100}%
        Upload % of advertised: {floatfmt(result['average']['upload'] / SETTINGS['purchased']['upload']) * 100}%

-------------------------------------------------------------------------------------------  

Please feel free to contact me directly using the contact information associated withe account below if you have any questions.

    """
    log(message)

    _result = send_mailgun(sender, receiver, subject, message)
    
    if _result.status_code == 200:
        log('Success')
    else:
        log('Failed.')


def floatfmt(value):
    return float("{:.2f}".format(value))


def send_mailgun(sender, receiver, subject, message):
    key = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN')
    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", key),
		data={
            "from": SETTINGS['from'],
			"to": SETTINGS['to'],
			"subject": subject,
			"text": message })

def load_data():
    
    data = []

    directory = os.path.join(os.path.dirname(__file__), SETTINGS["data"])
    file_name = f'results.json'
    file = os.path.join(directory, file_name)

    try:
        with open(file) as json_file:
            json_data = json.load(json_file)
            data = json_data
    except:
        pass

    return data

def save_data(result):
    data = []

    directory = os.path.join(os.path.dirname(__file__), SETTINGS["data"])
    file_name = f'results.json'
    file = os.path.join(directory, file_name)

    data = load_data()
    data.append(result)

    with open(file, 'w') as outfile:
        json.dump(data, outfile)
    
def get_results():
    
    out = subprocess.Popen(['speedtest', '--server', '16100', '--json', '--share'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    result = stdout.decode()

    data = json.loads(result)
    
    return data

def get_timestamp():
    date = datetime.now()
    tz_string = os.getenv('DEFAULT_TZ', 'America/Nassau')
    timezone = pytz.timezone(tz_string)
    date_aware = timezone.localize(date)
    date_string = date_aware.strftime('%d %B %Y at %H:%M %p')
    return date_string

def parse_results(result: dict):

    upload = floatfmt(result['upload'] / 1000000)
    download = floatfmt(result['download'] / 1000000)
    ping = floatfmt(result['ping'])

    return {

        'isp': result['client']['isp'],
        'ip': result['client']['ip'],


        'upload': upload,
        'download': download,
        'ping': ping,

        'bytes_sent': floatfmt(result['bytes_sent']),
        'bytes_received': floatfmt(result['bytes_received']),
        'timestamp': result['timestamp'],
        'share': result['share'],
        
        'server': result['server']['sponsor'],
        'host': result['server']['host'],

        'expected': {
            'download': floatfmt(SETTINGS['expected']['low'] * SETTINGS['purchased']['download']),
            'upload': floatfmt(SETTINGS['expected']['low'] * SETTINGS['purchased']['upload'])
        },
    }

def calculate_averages(data):

    holder = {
        'download': [],
        'upload': [],
        'ping': []
    }
    for d in data:
        holder['download'].append(d['download'])
        holder['upload'].append(d['upload'])
        holder['ping'].append(d['ping'])
    
    result = {
        'download': floatfmt(mean(holder['download'])),
        'upload': floatfmt(mean(holder['upload'])),
        'ping': floatfmt(mean(holder['ping']))
    }

    return result

def calculate_days():
    date_opened = datetime.strptime(SETTINGS['date_opened'], '%m-%d-%Y')
    days = (datetime.today() - date_opened).days
    return days

def run():
    results = get_results()
    result = parse_results(results)

    save_data(result)

    data = load_data()
    averages = calculate_averages(data)

    result['average'] = averages

    send_result(result)

run()


