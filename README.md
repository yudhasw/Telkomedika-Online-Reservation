<a id="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/yudhasw/Telkomedika-Online-Reservation">
    <img src="/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Telkomedika Online Reservation</h3>

  <p align="center">
    Website reservasi online layanan Telkomedika
    <br />
    <a href="https://github.com/yudhasw/Telkomedika-Online-Reservation"><strong>Explore the docs »</strong></a>
    <br />
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>📚 Table of Contents</summary>
  <ol>
    <li>
      <a href="#-about-the-project">⭐ About The Project</a>
    </li>
    <li><a href="#-feature">📋 Feature</a></li>
    <li><a href="#-tech-stack">⚡ Tech Stack</a></li>
    <li>
      <a href="#-getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#setup-environtment">Setup Environment</a></li>
        <li><a href="#run-the-project">Run The Project</a></li>
      </ul>
    </li>
    <li><a href="#-team">Team</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## ⭐ About The Project
Telkomedika Online Reservation adalah aplikasi berbasis web Reservasi Jadwal Pemeriksaan Dokter secara Online di Telkom Medika dirancang untuk memudahkan pasien dalam membuat jadwal reservasi pemeriksaan dengan dokter tanpa harus datang langsung ke Telkom Medika. Dengan adanya aplikasi ini, pasien dapat menghemat waktu dan meningkatkan efisiensi dalam pengolahan jadwal pemeriksaan oleh petugas Telkom Medika.


## 📋 Feature
- [ ] 📅 Reservation
    - [ ] Advanced Doctor Search : Patients can filter doctors by Polyclinic, Day, and Time.
    - [ ] Smart Date Selection: Patients pick a specific date, and the system automatically matches it with the doctor's available schedule.
    - [ ] Real-Time Quota System : The system calculates remaining slots accurately for specific dates, preventing overbooking.
- [ ] 📝 Data Management for Admin
    - [ ] Doctor Management
    - [ ] Polyclinic Management
    - [ ] Reservation Management
    - [ ] Doctor's Schedule Management


## ⚡ Tech Stack
* [![Flask][Flask.py]][Flask-url]
* [![Javascript][Javascript]][AzureSQL-url]
* [![TailwindCSS][Tailwind]][Tailwind-url]
* [![Azure SQL Database][AzureSQL]][AzureSQL-url]


<!-- GETTING STARTED -->
## 🚀 Getting Started
Berikut ini adalah _prerequisites_ dan  _installation_ jika ingin menjalankan proyek secara lokal.
Ikuti instruksi dibawah untuk mendapatkan _local copy_ dari proyek ini.

### Prerequisites
Before you begin, ensure you have met the following requirements:
1. Operating System
Windows (Recommended for SQL Server compatibility), macOS, or Linux.

2. Software & Tools
    - Python 3.10+: Make sure Python is installed and added to your system PATH.
    - Node.js & npm: Required to compile Tailwind CSS locally.
    - Git: To clone the repository.
    - Microsoft SQL Server: You need a running instance of SQL Server (Express or Developer edition is free for local use).

    - ODBC Driver 18 for SQL Server:
      This is mandatory for the application to connect to the database.
      [Download for Windows, macOS, and Linux here.](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17)

    - Database Management Tool (Optional but recommended):
      - SSMS (SQL Server Management Studio) or Azure Data Studio to visualize and manage your tables.

3. Knowledge
    - Basic understanding of how to use the Command Line or Terminal.

### Installation

1. Clone repository
   ```sh
   git clone https://github.com/yudhasw/Telkomedika-Online-Reservation.git
   ```
2. Buat Virtual Environment Python
   ```sh
   python -m venv .venv
   ```
   Aktifkan Environment
   ```sh
   .venv\Scripts\activate
   ```
4. Install Dependencies Python
   ```sh
   pip install -r requirements.txt
   ```
5. Install Dependencies NPM
   ```sh
   npm install
   ```
### Setup Environment
1. Make .env File
2. Copy this Code and fill it with your own data.
   ```sh
   SERVER_NAME=YourServerName
   DATABASE_NAME=YourDatabaseName
   DB_USERNAME=YourDatabaseUsername
   DB_PASSWORD=password_rahasia
   SECRET_KEY=random_secret_key
   MAIL_USERNAME=email@gmail.com
   MAIL_PASSWORD=app_password_google
   ```
### Run the Project
   ```sh
   npm run dev
   ```

## 👨🏻‍💻 Team
* Fransiskus Harris Berliandu 				    103012330401 
* Mohammad Narendra Rasendriya Narayana		103012300209 
* Daisaq Hadya Albar                      103012300158 
* Muhammad Nazriel Ihram                  103012300269 
* Yudha Setiawan Wicaksono                103012300480
<br />
<a href="https://github.com/yudhasw/Telkomedika-Online-Reservation/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yudhasw/Telkomedika-Online-Reservation" alt="contrib.rocks image" />
</a>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[product-screenshot]: images/screenshot.png
<!-- Shields.io badges. You can a comprehensive list with many more badges at: https://github.com/inttter/md-badges -->
[Flask.py]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/stable/
[Tailwind]: https://img.shields.io/badge/Tailwind_CSS-grey?style=for-the-badge&logo=tailwind-css&logoColor=38B2AC
[Tailwind-url]: https://tailwindcss.com/
[AzureSQL]: https://img.shields.io/badge/Azure%20SQL%20Database-0078D7?style=for-the-badge&logo=mirosoftazure&logoColor=white
[AzureSQL-url]: https://azure.microsoft.com/id-id/products/azure-sql/database
[Javascript]: https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black
[Javascript-url]: https://www.javascript.com/
