from flask import Flask, jsonify  
import spider
app = Flask(__name__)  
@app.route('/', methods=['GET'])  
@app.route('/recommend', methods=['GET'])  
def get_recommend():  
    data=spider.recommandation_algorithm(1)
    return jsonify(data)  
if __name__ == '__main__':  
    app.run(debug=True,port=9800)