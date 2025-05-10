from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import markdown

# Initialize Flask app
app = Flask(__name__)

# Load API keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get all raw material entries from dynamic form
        materials = request.form.getlist('material[]')
        sources = request.form.getlist('source[]')
        destinations = request.form.getlist('destination[]')
        routes = request.form.getlist('route[]')
        dates = request.form.getlist('date[]')

        supply_chain_entries = []
        for i in range(len(materials)):
            supply_chain_entries.append({
                "material": materials[i],
                "source": sources[i],
                "destination": destinations[i],
                "route": routes[i],
                "date": dates[i]
            })

        # Build dynamic prompt
        prompt = f"""
        You are a senior supply chain strategist with expertise in logistics, cost modeling, and sustainability for consumer textiles. Analyze this real-world cotton T-shirt supply chain using industry-level depth and specificity.

        Analyze the following supply chain components:

        {supply_chain_entries}

        Focus areas:
        - Consider **current political conditions**, **weather forecasts**, and **supply chain disruptions** on specific dates.
        - Include **real-time cost impacts**, **alternative sourcing** for materials, and **impact of route changes**.
        - Provide specific recommendations for **cost-saving opportunities**, **sustainability improvements**, and **resilience strategies**.

        Your response should include:
        - **Risk Assessment**: Specific geopolitical, climatic, infrastructure, and supplier concentration risks, with examples of **current events** that may affect the supply chain.
        - **Optimization**: Detailed suggestions for cost optimization, **route changes**, and **inventory management**.
        - **Granular Cost Analysis**: Breakdown of costs for each stage of the supply chain, including raw material, transportation, inventory, and manufacturing. Show both baseline and optimized costs.
        - **Sustainability Impact**: CO₂, water, and chemical usage estimates per stage of production and transport.
        - **Resilience Score**: A quantifiable improvement before and after applying your recommendations.
         - Rate resilience out of 10 based on:
             - Supplier diversity (weight: 30%)
             - Route redundancy (20%)
             - Digital visibility (20%)
             - Inventory buffers (15%)
             - Response time to disruption (15%)
           - Show **score formula and reasoning**
           - Summarize how proposed changes improve resilience

        Avoid generalizations or placeholders; provide concrete, actionable insights with estimated numbers and real examples.
        """

        # Use gpt-3.5-turbo for analysis
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful supply chain analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        analysis = response['choices'][0]['message']['content'].strip()

        # Convert markdown response to HTML
        html_analysis = markdown.markdown(analysis)

        return render_template('results.html', analysis=html_analysis)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
