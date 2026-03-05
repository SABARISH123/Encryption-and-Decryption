Encryption and Decryption Burp Extension

This extension helps encrypt and decrypt request/response payloads directly inside Burp Suite.
It is useful when testing applications where client-side encryption is implemented before sending requests to the server.

**Prerequisites**
Before installing the extension, ensure the following requirements are met:
Burp Suite (Community or Professional Edition)
Jython Standalone JAR file
**Download Jython from:**
https://www.jython.org/download

**Installing the Extension**
Follow the steps below to load the extension into Burp Suite:
1. Configure Jython in Burp
      Open Burp Suite
      Navigate to
       Extensions → Settings → Python Environment
Add the downloaded jython-standalone.jar file

2. Load the Extension
      Download the provided .py extension file
      Navigate to
        Extensions → Installed → Add
        Configure the following:
          Field	Value
          Extension Type	Python
          Extension File	Upload the .py file
          Click Next

If loaded successfully, Burp will display a success message and the extension will appear under the Installed Extensions tab.

**Purpose of the Tool**
Many modern applications implement client-side encryption before sending requests to the server.

The workflow usually looks like this:
  Client → Encrypt request payload → Send to server
  Server → Decrypt → Process request
  Server → Encrypt response → Send to client
  Client → Decrypt response → Display data

To perform this encryption/decryption, the client-side application contains cryptographic instructions, such as:
  Encryption algorithm
  Encryption mode
  Padding scheme
  Encryption key
  Initialization Vector (IV)

These values are usually found inside JavaScript files used by the application.

Sometimes:
  The key is hardcoded (which is a serious security vulnerability).
  The key or parameters may be obfuscated using nested functions or encoding techniques.

This extension helps replicate the encryption/decryption logic inside Burp Suite, allowing security testers to inspect and manipulate encrypted traffic.

The extension currently supports the following encryption algorithms and modes:

**Supported Algorithms**
DES
2DES
AES

**Supported AES Modes**
AES ECB
AES CBC
AES CFB
AES OFB
AES CTR

**Future updates will include support for:**
AES GCM

**Input Fields**
The extension requires the following parameters:
  Field	Description
  Algorithm	Encryption algorithm used
  Mode	Encryption mode used
  Padding	Padding scheme used
  Key	Encryption key
  IV / Nonce	Initialization vector or nonce
  Payload	Encrypted or plaintext payload
  Key Format	Format of the key (Hex/Base64/UTF-8 etc.)
  IV Format	Format of the IV
  Payload Encoding	Encoding format of the payload

**Steps to Use the Extension**
1. Select Encryption Algorithm
    Choose the algorithm used by the application.
    Example:
    AES
    DES
2. Select Mode and Padding
    Choose the encryption mode.
    Example:
    CBC
    ECB
    CTR
    CFB
    OFB
    Note:
    CBC mode requires padding
    Other modes usually do not require padding
3. Provide Encryption Key
    Enter the encryption key used by the application.
    Then select the format of the key, such as:
      Hex
      Base64
      UTF-8
4. Provide IV / Nonce
     Enter the Initialization Vector (IV) or Nonce.
     Select the format accordingly.
5. Provide Payload
     There are two methods to provide the payload.
     Method 1 (Recommended)
      Select the encrypted payload inside Burp Suite
      Right click
      Navigate to:
      Extensions → Universal Crypto → Send to Crypto
      This will automatically send the selected payload to the extension.
     Method 2
      Copy the encrypted payload manually
      Paste it into the Payload input field in the extension
6. Select Payload Encoding
      Choose the encoding format used for the payload.
      Example:
      Base64
      Hex
      UTF-8
7. Decrypt or Encrypt
     Click Decrypt or Encrypt
**Output**
  1. If the operation is successful, the result will be displayed in the Output Panel.
  2. If any error occurs, the details will appear in the Debug Panel.
