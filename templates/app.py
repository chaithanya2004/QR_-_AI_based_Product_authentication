{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "26f66f6f-3b35-4963-ba58-7fb91f0c7d9d",
   "metadata": {},
   "outputs": [],
   "source": [
    "from flask import Flask, render_template, request\n",
    "import pandas as pd\n",
    "import pickle\n",
    "import numpy as np\n",
    "\n",
    "app = Flask(__name__)\n",
    "\n",
    "# Load trained ML model\n",
    "model = pickle.load(open('model/waste_model.pkl', 'rb'))\n",
    "\n",
    "# Load inventory dataset\n",
    "df = pd.read_csv('data/grocery_inventory.csv')\n",
    "\n",
    "@app.route(\"/\", methods=['GET', 'POST'])\n",
    "def index():\n",
    "    predictions = []\n",
    "    if request.method == 'POST':\n",
    "        # Prepare features for prediction\n",
    "        X = df.drop(columns=['Date','Expiry_Date','Quantity_Sold','Unsold_Quantity'])\n",
    "        y_pred = model.predict(X)\n",
    "        df['Predicted_Unsold'] = y_pred\n",
    "        df['Action'] = df['Predicted_Unsold'].apply(lambda x: 'Apply Discount/Combo/Donate' if x > 5 else 'No Action')\n",
    "        predictions = df[['Item_Name', 'Stock_Quantity', 'Predicted_Unsold', 'Action']].to_dict(orient='records')\n",
    "        \n",
    "    return render_template(\"index.html\", predictions=predictions)\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    app.run(debug=True)\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
