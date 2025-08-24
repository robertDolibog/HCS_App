# Hybrid Cloud Storage API

This repository contains a **Python API backend**, which can be run using Docker.  
Additionally, it includes a **classification comparison module** to evaluate different file classifiers.

The API provides the following endpoints:

- **POST** `/sync`
- **GET** `/all-files`

---

## Endpoints

### `POST /sync`
Establishes a connection to the configured storage backends:
- **Local environment** → sample folder: `/backend/HCS`
- **FTPS server** → has to contain a folder named `HCS` in the parent directory
- **Dropbox account** → the App folder needs to contain a separate folder named `HCS`


Further, the files from these backends are compared against each other and classified.


**Output:** Returns the number of all processed files. To get these files, use the following endpoint:


### `GET /all-files`
Retrieves a list of all files across the connected storage backends.

---

## Setup

### Prerequisites
Before running the backend, make sure you have:

1. **FTPS server setup**  
   - If you use a FritzBox, you can follow this guide:  
     [FritzBox NAS Setup Guide](https://fritz.com/service/wissensdatenbank/dok/FRITZ-Box-7530-AX/508_NAS-System-im-FRITZ-Heimnetz-einsetzen)
   - The FTPS server needs to contain a folder named `HCS` in the parent directory.  

2. **Dropbox developer application**  
   - Create a Dropbox app that links to any folder. This folder needs to contain a directory named **HCS**.  
   - Tutorial: [Dropbox Developer Getting Started](https://www.dropbox.com/developers/reference/getting-started#app%20console)

3. **Environment variables**  
   - Create a `.env` file inside the `/backend` directory.  
   - Add the following values:

     ```env
     FTPS_HOST=<url-to-host-ftpServer>
     FTPS_PORT=<port>
     FTPS_USER=<username>
     FTPS_PASSWORD=<password>

     DROPBOX_ACCESS_TOKEN=<newly generated Dropbox access token>
     ```

   **Note:** Dropbox access tokens are valid for only **3 hours**.

---

### Running with Docker

Once your `.env` file is configured, start the backend with:

```bash
docker compose up
```

The API should now be available at `http://localhost:5000`.

---

## Classification Comparison

In addition to the backend, this repository contains scripts to **test and compare different classifiers**.

### Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate a dataset**
   ```bash
   python generate_dataset.py
   ```
   - You can specify a reproducibility seed.  
   - The seed used in the thesis experiments was: `123456`, but any seed can be used.

3. **Run the classification**
   ```bash
   python classification.py
   ```

This will execute the comparison between the implemented classifiers and output the performance results.

---

## Notes
- Dropbox tokens must be refreshed regularly.  
- The **classification experiments** are intended for local execution only and are not part of the Dockerized backend.