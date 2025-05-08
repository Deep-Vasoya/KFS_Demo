You can install the necessary Python packages using pip (see "How to Run").  You will also need a working installation of Google Chrome.

## How to Run

1.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**

    ```bash
    .\venv\Scripts\activate.bat
    ```

3.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    pip install setuptools
    ```

4.  **Run the Flask application:**

    ```bash
    python app.py
    ```

5.  **Important: Chrome Extension Path**

    * In `app.py`, the `buster_extension_path` variable is hardcoded with a specific path to the Buster Captcha Solver extension:

        ```python
        buster_extension_path = r"C:\Users\ASUS TUF\AppData\Local\Google\Chrome\User Data\Default\Extensions\mpbjkejclgfgadiemmefgebjfooflfhl\3.1.0_0"
        ```

    * **You MUST change this path to the correct location of the Buster extension on your system.** To find the extension path:
        1.  Go to `chrome://extensions/` in your Chrome browser.
        2.  Find the "Buster: Captcha Solver for Humans" extension.
        3.  Copy the "ID" (a long string of characters).
        4.  The extension path will typically be in a directory like:
            * Windows:  `C:\Users\[YourUsername]\AppData\Local\Google\Chrome\User Data\Default\Extensions\[ExtensionID]\[VersionNumber]`
        * Replace the hardcoded path in `app.py` with your system's correct path.

6.  **Access the application:**

    * Open your web browser and go to the address provided by the Flask development server (usually `http://127.0.0.1:5000/`).
