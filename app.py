from flask import Flask, render_template, request, jsonify
import requests
import re
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Replace 'YOUR_VIRUSTOTAL_API_KEY' with your actual VirusTotal API key
API_KEY = 'adde1f1fc8d8369ce5e5b65e5711537d0219a6ff4d53d2db4f8fd00ef3c8a1c9'
VIRUSTOTAL_API_URL = 'https://www.virustotal.com/vtapi/v2/url/report'

fake_words = [
    r'\bmiracl[ae] solution\b',
    r'\bguaranteed results\b',
    r'\bget rich quick\b',
    r'\blife-changing\b',
    r'\babsolutely love it\b',
    r'\bbest ever\b',
    r'\bcan\'t live without it\b',
    r'\bperfect in every way\b',
    r'\bmoney-back guarantee with no questions asked\b',
    r'\blimited time offer\b',
    r'\bexclusive discount\b',
    r'\btry it now\b',
    r'\bonce in a lifetime opportunity\b',
    r'\bact fast\b',
    r'\binstant results\b',
    r'\bsecret formula\b',
    r'\brevolutionary\b',
    r'\bbreakthrough\b',
    r'\bamazingly effective\b',
    r'\bnever seen anything like it\b',
    r'\bmagical product\b',
    r'\btransformative\b',
    r'\bunbelievable benefits\b',
    r'\btoo good to be true\b',
    r'\bovernight success\b',
    r'\bquick fix\b',
    r'\beffortless solution\b',
    r'\bone-of-a-kind\b',
    r'\bmust-have\b',
    r'\bhidden gem\b',
    r'\binstant gratification\b',
    r'\bno risk, all reward\b',
    r'\b100% satisfaction guaranteed\b',
    r'\bmind-blowing results\b',
    r'\blife-altering\b',
    r'\bunparalleled quality\b',
    r'\bunmatched performance\b',
    r'\bincredible value\b',
    r'\bgame-changer\b',
    r'\bdream come true\b',
    r'\bastounding\b',
    r'\bultimate solution\b',
    r'\bunbeatable offer\b',
    r'\bact now or regret later\b',
    r'\bout-of-this-world\b',
    r'\birresistible deal\b',
    r'\bcan\'t beat the price\b',
    r'\bunimaginable benefits\b',
    r'\babsolutely flawless\b',
    r'\bwish I found it sooner\b',
]

genuine_words = [
    r'\bdetailed analysis\b',
    r'\bspecific features\b',
    r'\bbalanced perspective\b',
    r'\bhonest evaluation\b',
    r'\bcomparative insights\b',
    r'\bauthentic experience\b',
    r'\bpractical observations\b',
    r'\breal-world usage\b',
    r'\bthoughtful commentary\b',
    r'\bin-depth review\b',
    r'\bcomprehensive assessment\b',
    r'\bhonest feedback\b',
    r'\bnoteworthy qualities\b',
    r'\buser-friendly interface\b',
    r'\bvalue for money\b',
    r'\bimpressive functionality\b',
    r'\bpractical applications\b',
    r'\breliable performance\b',
    r'\bversatile usage\b',
    r'\bresponsive customer service\b',
    r'\bwell-crafted design\b',
    r'\bdurability\b',
    r'\blong-lasting\b',
    r'\bseamless integration\b',
    r'\bintuitive controls\b',
    r'\benhances productivity\b',
    r'\bsolid construction\b',
    r'\bsuperior craftsmanship\b',
    r'\bconsistent results\b',
    r'\bhigh-quality materials\b',
    r'\bpractical benefits\b',
    r'\benhances efficiency\b',
    r'\bseamless user experience\b',
    r'\baddresses needs effectively\b',
    r'\beffective solution\b',
    r'\bworth the investment\b',
    r'\bclear advantages\b',
    r'\buser-friendly features\b',
    r'\bnotable improvements\b',
    r'\breliable results\b',
    r'\btrustworthy brand\b',
    r'\bengaging experience\b',
    r'\bimpressive performance\b',
    r'\bsurpasses expectations\b',
    r'\breliable warranty\b',
    r'\bthoughtful design\b',
    r'\bexemplary customer support\b',
    r'\btailored solutions\b',
    r'\bresponsive to feedback\b',
    r'\btransparent policies\b',
]


# Sample database of products
products = {
    "12345": {"name": "Paracetamol", "price": 10.99},
    "67890": {"name": "Ibuprofen", "price": 19.99},
    "13579": {"name": "Aspirin", "price": 15.49},
    "24680": {"name": "Amoxicillin", "price": 8.99},
    "11111": {"name": "Ciprofloxacin", "price": 25.99},
    "22222": {"name": "Loratadine", "price": 14.99},
    "33333": {"name": "Omeprazole", "price": 9.49},
    "44444": {"name": "Prednisone", "price": 12.99},
    "55555": {"name": "Metformin", "price": 17.99},
    "66666": {"name": "Azithromycin", "price": 21.99},
    "77777": {"name": "Ranitidine", "price": 7.49},
    "88888": {"name": "Doxycycline", "price": 13.99},
    "99999": {"name": "Simvastatin", "price": 18.99},
    "10101": {"name": "Warfarin", "price": 22.99},
    "12121": {"name": "Diazepam", "price": 6.99},
    "13131": {"name": "Sertraline", "price": 11.49},
    "14141": {"name": "Hydrochlorothiazide", "price": 16.99},
    "15151": {"name": "Albuterol", "price": 23.99},
    "16161": {"name": "Atorvastatin", "price": 28.99},
    "17171": {"name": "Citalopram", "price": 5.99}
}
    # Add more medicines here if needed
   
# Sample database
transactions = [
    {"Entry": 1, "Device Code": "ABC123", "Transaction Amount": 50.00, "Location": "New York", "Date": "2024-03-15"},
    {"Entry": 2, "Device Code": "XYZ456", "Transaction Amount": 30.00, "Location": "Los Angeles", "Date": "2024-3-10"},
    {"Entry": 3, "Device Code": "ABC123", "Transaction Amount": 2004.00, "Location": "New York", "Date": "2024-03-14"},
    {"Entry": 4, "Device Code": "DEF789", "Transaction Amount": 75.00, "Location": "Chicago", "Date": "2024-3-05"},
    {"Entry": 5, "Device Code": "ABC123", "Transaction Amount": 1000.00, "Location": "New York", "Date": "2024-03-14"},
    {"Entry": 6, "Device Code": "GHI012", "Transaction Amount": 40.00, "Location": "San Francisco", "Date": "2024-3-14"},
    {"Entry": 7, "Device Code": "ABC123", "Transaction Amount": 6008.00, "Location": "New York", "Date": "2024-03-22"},
    {"Entry": 8, "Device Code": "JKL345", "Transaction Amount": 60.00, "Location": "Miami", "Date": "2024-03-15"},
    {"Entry": 9, "Device Code": "MNO678", "Transaction Amount": 55.00, "Location": "Seattle", "Date": "2024-03-14"},
    {"Entry": 10, "Device Code": "ABC123", "Transaction Amount": 2000.00, "Location": "New York", "Date": "2024-03-10"},
    {"Entry": 11, "Device Code": "PQR901", "Transaction Amount": 45.00, "Location": "Boston", "Date": "2024-03-12"},
    {"Entry": 12, "Device Code": "ABC123", "Transaction Amount": 4000.00, "Location": "New York", "Date": "2024-03-9"},
    {"Entry": 13, "Device Code": "STU234", "Transaction Amount": 70.00, "Location": "Atlanta", "Date": "2024-02-8"},
    {"Entry": 14, "Device Code": "ABC123", "Transaction Amount": 6000.00, "Location": "New York", "Date": "2024-03-7"},
    {"Entry": 15, "Device Code": "VWX567", "Transaction Amount": 65.00, "Location": "Dallas", "Date": "2024-02-6"},
]

def classify_review(review):
    try:
        fake_matches = any(re.search(word, review, re.IGNORECASE) for word in fake_words)
        genuine_matches = any(re.search(word, review, re.IGNORECASE) for word in genuine_words)

        if fake_matches and not genuine_matches:
            return "Fake Review"
        elif genuine_matches and not fake_matches:
            return "Genuine Review"
        else:
            return "(Neutral) Classification Uncertain"
    except Exception as e:
        return "Error: " + str(e)

def find_frequent_transactions(transactions, device_code, time_period):
    today = datetime.now()
    start_date = today - timedelta(days=time_period*30)
    filtered_transactions = [transaction for transaction in transactions if transaction["Device Code"] == device_code and datetime.strptime(transaction["Date"], "%Y-%m-%d") >= start_date]
    return len(filtered_transactions), filtered_transactions

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_url', methods=['POST'])
def check_url():
    url = request.form.get('url')

    params = {'apikey': API_KEY, 'resource': url}
    response = requests.get(VIRUSTOTAL_API_URL, params=params)
    result = response.json()

    return jsonify(result)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form["code"]
        if code in products:
            product = products[code]
            return f"Product: {product['name']}, Price: ${product['price']}"
        else:
            return "Invalid product code"
    return render_template("index.html")

@app.route('/classify', methods=['POST'])
def classify():
    review = request.json.get('review')
    classification = classify_review(review)
    return jsonify({'result': classification})

@app.route('/analyze', methods=['POST'])
def analyze():
    device_code = request.form['device_code']
    time_period = int(request.form['time_period'])

    device_count, suspicious_transactions = find_frequent_transactions(transactions, device_code, time_period)

    return render_template('result.html', device_code=device_code, time_period=time_period, device_count=device_count, suspicious_transactions=suspicious_transactions)

if __name__ == '__main__':
    app.run(debug=True)
