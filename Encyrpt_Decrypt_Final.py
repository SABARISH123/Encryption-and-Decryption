# -*- coding: utf-8 -*-

from burp import IBurpExtender, ITab, IContextMenuFactory
from javax.swing import (
    JPanel, JLabel, JTextField, JComboBox,
    JButton, JScrollPane, JTextArea,
    BoxLayout, JMenuItem
)
from java.util import ArrayList
from javax.crypto import Cipher
from javax.crypto.spec import SecretKeySpec, IvParameterSpec
import base64
import binascii
import json
import traceback


class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Universal Crypto")

        self.build_ui()

        callbacks.addSuiteTab(self)
        callbacks.registerContextMenuFactory(self)

    # ================= UI =================

    def build_ui(self):

        self.panel = JPanel()
        self.panel.setLayout(BoxLayout(self.panel, BoxLayout.Y_AXIS))

        configPanel = JPanel()

        configPanel.add(JLabel("Algorithm"))
        self.algoBox = JComboBox(["AES", "DES", "DESede"])
        configPanel.add(self.algoBox)

        configPanel.add(JLabel("Mode"))
        self.modeBox = JComboBox(["CBC", "ECB", "CFB", "OFB", "CTR"])
        configPanel.add(self.modeBox)

        configPanel.add(JLabel("Padding"))
        self.padBox = JComboBox(["PKCS5Padding", "NoPadding"])
        configPanel.add(self.padBox)

        self.panel.add(configPanel)

        keyPanel = JPanel()
        keyPanel.add(JLabel("Key"))
        self.keyField = JTextField(40)
        keyPanel.add(self.keyField)

        keyPanel.add(JLabel("Key Format"))
        self.keyFormat = JComboBox(["Base64", "Hex", "UTF-8"])
        keyPanel.add(self.keyFormat)

        self.panel.add(keyPanel)

        ivPanel = JPanel()
        ivPanel.add(JLabel("IV / Nonce"))
        self.ivField = JTextField(40)
        ivPanel.add(self.ivField)

        ivPanel.add(JLabel("IV Format"))
        self.ivFormat = JComboBox(["Base64", "Hex", "UTF-8"])
        ivPanel.add(self.ivFormat)

        self.panel.add(ivPanel)

        payloadPanel = JPanel()
        payloadPanel.add(JLabel("Payload Encoding"))
        self.payloadEncoding = JComboBox(["Base64", "Hex", "UTF-8"])
        payloadPanel.add(self.payloadEncoding)

        self.panel.add(payloadPanel)

        self.panel.add(JLabel("Input"))
        self.inputArea = JTextArea(10, 120)
        self.inputArea.setLineWrap(True)
        self.inputArea.setWrapStyleWord(True)
        self.panel.add(JScrollPane(self.inputArea))

        btnPanel = JPanel()
        btnPanel.add(JButton("Decrypt", actionPerformed=self.decrypt))
        btnPanel.add(JButton("Encrypt", actionPerformed=self.encrypt))
        self.panel.add(btnPanel)

        self.panel.add(JLabel("Output"))
        self.outputArea = JTextArea(12, 120)
        self.outputArea.setLineWrap(True)
        self.outputArea.setWrapStyleWord(True)
        self.panel.add(JScrollPane(self.outputArea))

        self.panel.add(JLabel("Debug"))
        self.debugArea = JTextArea(6, 120)
        self.debugArea.setLineWrap(True)
        self.panel.add(JScrollPane(self.debugArea))

    # ================= TAB =================

    def getTabCaption(self):
        return "Crypto"

    def getUiComponent(self):
        return self.panel

    # ================= RIGHT CLICK =================

    def createMenuItems(self, invocation):
        self.invocation = invocation
        menu = ArrayList()
        menu.add(JMenuItem("Send to Crypto", actionPerformed=self.sendToCrypto))
        return menu

    def sendToCrypto(self, event):
        try:
            msg = self.invocation.getSelectedMessages()[0]
            bounds = self.invocation.getSelectionBounds()

            context = self.invocation.getInvocationContext()

            if context in [
                self.callbacks.CONTEXT_MESSAGE_EDITOR_REQUEST,
                self.callbacks.CONTEXT_MESSAGE_VIEWER_REQUEST
            ]:
                content = msg.getRequest()
            else:
                content = msg.getResponse()

            selected = self.helpers.bytesToString(content[bounds[0]:bounds[1]])
            self.inputArea.setText(selected.strip())

        except:
            self.debugArea.setText(traceback.format_exc())

    # ================= HELPERS =================

    def normalize_base64(self, value):
        # Auto-detect URL-safe Base64
        if '-' in value or '_' in value:
            value = value.replace('-', '+').replace('_', '/')
        return value

    def decode_value(self, value, fmt):

        if fmt == "Base64":
            value = self.normalize_base64(value)
            return base64.b64decode(value)

        elif fmt == "Hex":
            return binascii.unhexlify(value)

        else:
            return value.encode("utf-8")

    def encode_value(self, value, fmt):

        if fmt == "Base64":
            return base64.b64encode(value).decode()

        elif fmt == "Hex":
            return binascii.hexlify(value).decode()

        else:
            return value.decode("utf-8")

    def build_cipher(self, modeType):

        algo = self.algoBox.getSelectedItem()
        mode = self.modeBox.getSelectedItem()
        padding = self.padBox.getSelectedItem()

        transformation = "%s/%s/%s" % (algo, mode, padding)

        keyBytes = self.decode_value(
            self.keyField.getText(),
            self.keyFormat.getSelectedItem()
        )

        keySpec = SecretKeySpec(keyBytes, algo)
        cipher = Cipher.getInstance(transformation)

        if mode != "ECB":
            ivBytes = self.decode_value(
                self.ivField.getText(),
                self.ivFormat.getSelectedItem()
            )
            cipher.init(modeType, keySpec, IvParameterSpec(ivBytes))
        else:
            cipher.init(modeType, keySpec)

        return cipher

    # ================= DECRYPT =================

    def decrypt(self, event):
        try:
            self.debugArea.setText("")

            cipher = self.build_cipher(Cipher.DECRYPT_MODE)

            raw = self.decode_value(
                self.inputArea.getText().strip(),
                self.payloadEncoding.getSelectedItem()
            )

            result = cipher.doFinal(raw)

            plain = ''.join([chr((b + 256) % 256) for b in result])

            try:
                parsed = json.loads(plain)
                plain = json.dumps(parsed, indent=4)
            except:
                pass

            self.outputArea.setText(plain)

        except:
            self.debugArea.setText(traceback.format_exc())

    # ================= ENCRYPT =================

    def encrypt(self, event):
        try:
            self.debugArea.setText("")

            cipher = self.build_cipher(Cipher.ENCRYPT_MODE)

            raw = self.inputArea.getText().encode("utf-8")
            result = cipher.doFinal(raw)

            pybytes = bytearray((b + 256) % 256 for b in result)

            encoded = self.encode_value(
                pybytes,
                self.payloadEncoding.getSelectedItem()
            )

            self.outputArea.setText(encoded)

        except:
            self.debugArea.setText(traceback.format_exc())