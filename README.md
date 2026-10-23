# 🩸 Blood Bank Management System

## 📌 Project Overview

The Blood Bank Management System is a Python-based web application developed using Streamlit and SQLite. It helps manage blood donations, blood requests, donors, patients, and blood stock.

## ✨ Features

- 📊 Dashboard with blood stock summary and key metrics
- 🩸 Blood donation submission
- 📋 Donation approval and rejection
- 🏥 Blood request submission
- 📄 Blood request management
- 👥 Donors directory
- 🩺 Patients directory
- ⚙️ Blood stock management
- 📈 Blood stock visualization
- 💾 SQLite database integration

## 🛠️ Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Git and GitHub

## 📂 Project Structure

```text
bloodbank/
├── app.py
├── requirements.txt
├── .gitignore
├── manage.py
└── README.md
```

*Note: The structure above lists the main files. Other project files may also be present.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/bloodbank-management-system.git
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Open the project folder

```bash
cd bloodbank-management-system
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will usually open at:

`http://localhost:8501`

## 🗄️ Database

The application uses SQLite to store blood stock, donation records, blood requests, and related information. Database tables are initialized by the application when it starts.

## 🚀 Deployment

The Streamlit application can be deployed using Streamlit Community Cloud.

https://share.streamlit.io/

Select the GitHub repository and configure `app.py` as the main application file.

## 🎯 Project Objective

The objective of this project is to simplify blood bank operations by providing a centralized interface for managing blood donations, blood requests, and blood inventory.

## 👩‍💻 Author

Add your name here.

## 📄 License

This project is intended for educational and learning purposes.
