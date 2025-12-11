# SnapBudget

SnapBudget is a Python-based expense tracking application designed to streamline the process of recording receipt totals. It leverages Optical Character Recognition (OCR) to automatically extract total amounts from receipt images and stores the data securely in Google Sheets for permanent access. The application features a web interface built with Streamlit, optimized for both desktop and mobile use.

## Features

### Core Functionality
- **OCR Extraction**: Automatically detects and processes text from receipt images (JPG, PNG) to find the Total Amount.
- **Manual Verification**: Users can review and edit the extracted amount, date, and text before saving.
- **Categorization**: Assign categories (e.g., Food, Transport, Utilities) to expenses for better organization.

### Data Management
- **Cloud Storage**: All data is saved directly to a Google Sheet ("SnapBudget Expenses"), ensuring data persists across sessions and devices.
- **Dashboard**: A comprehensive dashboard displays total expenses for the current month and a visual chart of recent spending.
- **Full Control**: Users can edit or delete existing entries directly from the interface.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.8+**: The core programming language.
2.  **Tesseract OCR**: The engine used for text recognition. This is a system-level dependency.
    -   **Windows**: Download and install from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    -   *Note*: The application attempts to auto-detect Tesseract in `C:\Program Files\Tesseract-OCR`. If installed elsewhere, ensure it is added to your System PATH.

## Installation

1.  **Clone or Download the Repository**
    Navigate to the project directory in your terminal.

2.  **Install Python Dependencies**
    Run the following command to install required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

SnapBudget uses Google Sheets as its database. You must configure Google Cloud credentials to enable this.

1.  **Create a Google Service Account**
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Create a new project.
    -   Enable the **Google Sheets API** and **Google Drive API**.
    -   Create a **Service Account** and download its JSON key file.

2.  **Set Up Secrets**
    -   Create a folder named `.streamlit` in the project root.
    -   Inside it, create a file named `secrets.toml`.
    -   Paste the contents of your JSON key file into `secrets.toml` under the `[gcp_service_account]` section. Refer to `secrets.toml.example` in this repository for the exact format.

    > **SECURITY WARNING**: Never commit `.streamlit/secrets.toml` to GitHub or version control. This file contains your private API keys. The `.gitignore` file in this repository is configured to exclude it automatically.

3.  **Share the Spreadsheet**
    -   Create a new Google Sheet named **SnapBudget Expenses**.
    -   Share this sheet with the `client_email` address found in your Service Account JSON file (e.g., `service-account@project-id.iam.gserviceaccount.com`).
    -   Grant **Editor** permission.

## Deployment to Streamlit Cloud

You can safely deploy this app without exposing your credentials.

1.  **Push to GitHub**: Commit and push your code.
    -   *Note*: The `.streamlit/secrets.toml` file will **NOT** be uploaded because of the `.gitignore` file. This is expected and keeps your keys safe.

2.  **Deploy**:
    -   Go to [share.streamlit.io](https://share.streamlit.io/).
    -   Select your repository and branch.
    -   Click **Deploy**.

3.  **Configure Secrets in Cloud**:
    -   Your app will initially fail or show an error because it's missing the credentials. This is normal.
    -   In your app's dashboard, click **Manage App** (bottom right) -> **...** (three dots) -> **Settings** -> **Secrets**.
    -   Copy the content of your local `.streamlit/secrets.toml` file.
    -   Paste it into the Secrets text area on Streamlit Cloud and click **Save**.
    -   The app will automatically restart and connect securely.

## Usage

To start the application, run:

```bash
streamlit run app.py
```

The application will open in your default web browser.

### Navigation
-   **Upload & Extract**: The primary tab for adding new expenses. Upload a receipt, wait for extraction, verify the details, and click "Save Expense".
-   **Dashboard**: View your spending history. This tab allows you to visualize trends and manage (edit/delete) past entries.

## Troubleshooting

### Tesseract Not Found
If you receive an error stating Tesseract is missing:
1.  Verify Tesseract is installed on your computer.
2.  Restart your terminal/IDE to refresh environment variables.
3.  If installed in a custom location, add that directory to your System PATH.

### Google Sheets Error
If the app cannot find the spreadsheet:
1.  Ensure the Google Sheet is named exactly "SnapBudget Expenses".
2.  Verify you have shared the sheet with the correct Service Account email address.
3.  Check that `secrets.toml` is correctly formatted and located in the `.streamlit` folder.
